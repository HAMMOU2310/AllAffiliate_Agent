# FINAL DESIGN REVIEW — Research Foundation

**Reviewer:** Final Design Reviewer
**Date:** 2026-08-30
**Design Under Review:** `workspace/RESEARCH_FOUNDATION_ARCHITECTURE.md`
**Decision:** Tavily as first WebSearchProvider
**Task Type:** DESIGN-ONLY — No files created, no contracts modified

> **SUPERSEDED (2026-09-01):** This review originally approved Tavily as the first WebSearchProvider.
> The decision has been superseded by **OpenSERP OSS** — a self-hosted, MIT-licensed search API
> requiring no API key, no billing, and no subscription.
> See `providers/openserp_search_provider.py` for the current implementation.
> The `ResearchSource` protocol and evidence contract remain unchanged.

---

## 1. TAVILY SUITABILITY — VERIFIED

| Attribute | Fact | Suitable? |
|-----------|------|-----------|
| Free tier | 1,000 credits/month, no credit card | YES — zero-cost development |
| API type | Simple HTTP POST to `https://api.tavily.com/search` | YES — no SDK required |
| Authentication | Bearer token in header | YES — standard HTTP auth |
| Response format | `{results: [{title, url, content, score}]}` | YES — maps directly to evidence contract |
| Rate limits | Handled via 429 responses | YES — standard HTTP status codes |
| SDK available | `tavily-python` exists but NOT required | YES — HTTP-only approach works |
| Search depth | basic (1 credit), advanced (2 credits), fast, ultra-fast | YES — configurable cost/quality |
| Domain filtering | `include_domains`, `exclude_domains` | YES — future scope parameter |
| Content extraction | `include_raw_content` for full page content | YES — optional enrichment |
| Result scoring | `score` field (0-1 float) | YES — future quality filtering |
| Documentation | Complete OpenAPI spec at `docs.tavily.com` | YES — well documented |

**Tavily is suitable.** It has a free tier, simple HTTP API, clean response format, and is purpose-built for AI/agent use cases. No SDK dependency needed — raw `requests` calls suffice.

---

## 2. RESEARCHSOURCE CONTRACT — SUFFICIENT

The existing `ResearchSource` protocol:

```python
class ResearchSource(Protocol):
    def search(self, query: str, scope: str | None = None) -> Result:
        ...
```

**Is this sufficient? YES.**

Reasons:
1. `query` (str) maps directly to Tavily's `query` parameter
2. `scope` (str|None) can be mapped to Tavily's `topic` parameter (general/news/finance)
3. Return type `Result` with `data=[{source, title, content, kind}]` maps to Tavily's `results` array
4. ResearchService already handles normalization, deduplication, and error aggregation
5. No protocol change needed

**Scope mapping:**

| scope value | Tavily `topic` parameter |
|-------------|--------------------------|
| `None` or `"general"` | `"general"` |
| `"news"` | `"news"` |
| `"finance"` | `"finance"` |
| Any other value | `"general"` (fallback) |

---

## 3. EXACT PUBLIC INTERFACE

```python
class WebSearchProvider:
    """Provider-neutral web search adapter implementing ResearchSource."""

    def __init__(
        self,
        api_key_env: str = "TAVILY_API_KEY",
        search_depth: str = "basic",
        max_results: int = 5,
        include_answer: bool = False,
        include_raw_content: bool = False,
        timeout: int = 30,
    ) -> None:
        ...

    def search(self, query: str, scope: str | None = None) -> Result:
        """Execute a web search. Satisfies ResearchSource protocol."""
        ...
```

### Constructor Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `api_key_env` | str | `"TAVILY_API_KEY"` | Environment variable name for API key |
| `search_depth` | str | `"basic"` | Tavily search depth (basic/advanced/fast/ultra-fast) |
| `max_results` | int | `5` | Maximum results to return (1-20) |
| `include_answer` | bool | `False` | Include LLM-generated answer (future use) |
| `include_raw_content` | bool | `False` | Include full page content (future use) |
| `timeout` | int | `30` | HTTP request timeout in seconds |

### Method Signature

```python
def search(self, query: str, scope: str | None = None) -> Result:
```

This is EXACTLY the `ResearchSource.search()` signature. No adapter wrapper needed.

---

## 4. NORMALIZED RESULT STRUCTURE

### Input (Tavily API Response)

```json
{
  "query": "best solar panels 2026",
  "results": [
    {
      "title": "Best Solar Panels of 2026",
      "url": "https://example.com/solar-panels",
      "content": "Solar panels reduce energy costs by up to 50%...",
      "score": 0.92
    }
  ],
  "response_time": 1.23
}
```

### Output (Evidence for ResearchService)

```python
[
    {
        "source": "https://example.com/solar-panels",  # from results[].url
        "title": "Best Solar Panels of 2026",           # from results[].title
        "content": "Solar panels reduce energy costs...", # from results[].content
        "kind": "FACT",                                  # constant
    }
]
```

### Field Mapping

| Evidence Field | Tavily Source | Transformation |
|----------------|---------------|----------------|
| `source` | `results[].url` | None (direct copy) |
| `title` | `results[].title` | `.strip()` |
| `content` | `results[].content` | `.strip()` |
| `kind` | constant | Always `"FACT"` |

### Deduplication

Deduplication is handled by **ResearchService**, NOT WebSearchProvider. WebSearchProvider returns raw results from a single query. ResearchService deduplicates across multiple sources.

### Serialization

All fields are plain strings. JSON-serializable. No custom types.

---

## 5. ERROR/FAILURE MODEL

| HTTP Status | Tavily Error | WebSearchProvider Response |
|-------------|-------------|---------------------------|
| — | Missing API key | `Result.fail("Web search credentials are not configured.")` |
| 401 | Invalid API key | `Result.fail("Web search authentication failed.")` |
| 400 | Bad request | `Result.fail("Web search request is invalid.")` |
| 429 | Rate limit | `Result.fail("Web search rate limit exceeded.")` |
| 432 | Plan limit | `Result.fail("Web search plan limit exceeded.")` |
| 433 | PayGo limit | `Result.fail("Web search pay-as-you-go limit exceeded.")` |
| 500 | Server error | `Result.fail("Web search request failed.")` |
| timeout | Connection timeout | `Result.fail("Web search request timed out.")` |
| DNS | DNS resolution failure | `Result.fail("Web search request failed.")` |
| — | Malformed JSON | `Result.fail("Web search returned an invalid response.")` |
| — | Empty results | `Result.ok(data=[], message="No results found.")` |
| — | Unexpected exception | `Result.fail("Web search execution failed.")` |

**Empty results are NOT failures.** They are valid outcomes returning an empty list.

**No automatic retries.** ResearchService is fail-closed. A failed source stops all research. Retry logic, if needed, belongs in ResearchService (future enhancement).

---

## 6. CREDENTIAL MODEL

| Rule | Implementation |
|------|---------------|
| Source | `os.getenv(api_key_env)` |
| Default env var | `TAVILY_API_KEY` |
| Format | `tvly-xxxxxxxxxxxxxxxxxxxxx` (Tavily prefix) |
| Loading | Lazy — only when `search()` is called |
| Storage | Never stored in Result objects |
| Logging | Never logged |
| Git | `.env` in `.gitignore` |
| Tests | `unittest.mock.patch.dict(os.environ, ...)` |

---

## 7. TIMEOUT/RETRY/RATE-LIMIT POLICY

| Policy | Decision | Reason |
|--------|----------|--------|
| Timeout | 30 seconds default, configurable | Tavily basic search typically returns in 1-3s |
| Retry | NO automatic retries | Fail-closed; caller decides retry strategy |
| Rate limit | No client-side rate limiting | Tavily enforces server-side; we handle 429 |
| Backoff | Not implemented | No retries = no backoff needed |

---

## 8. TEST BOUNDARIES

| Category | Marker | Credentials | Network | Count |
|----------|--------|-------------|---------|-------|
| Unit tests | None | NO | NO | ~15 |
| Contract tests | None | NO | NO | ~3 |
| Integration tests | `@pytest.mark.integration` | YES | YES | ~2 |
| Real smoke | `@pytest.mark.integration` | YES | YES | 1 |

### Unit Tests (No credentials, no network)

| Test | What It Proves |
|------|----------------|
| `test_construction_default` | Default parameters work |
| `test_construction_custom` | Custom parameters are stored |
| `test_search_success` | Happy path: query → evidence |
| `test_search_normalizes_response` | Tavily response maps to evidence correctly |
| `test_search_empty_results` | Empty results return `Result.ok(data=[])` |
| `test_search_missing_credentials` | Missing env var returns failure |
| `test_search_invalid_credentials` | 401 returns failure |
| `test_search_network_timeout` | Timeout returns failure |
| `test_search_dns_failure` | DNS error returns failure |
| `test_search_server_error` | 500 returns failure |
| `test_search_rate_limit` | 429 returns failure |
| `test_search_malformed_response` | Bad JSON returns failure |
| `test_search_unexpected_exception` | Exception returns failure |
| `test_search_result_compatibility` | Result satisfies ResearchSource contract |
| `test_secret_not_in_result` | API key never in Result objects |
| `test_scope_mapping` | Scope values map to Tavily `topic` correctly |

### Contract Tests

| Test | What It Proves |
|------|----------------|
| `test_implements_research_source` | WebSearchProvider has `.search()` method |
| `test_method_signature_matches` | Signature matches Protocol |
| `test_return_type_is_result` | Returns Result object |

### Integration Tests

| Test | What It Proves |
|------|----------------|
| `test_real_tavily_search` | Real API call returns evidence |
| `test_research_service_with_provider` | End-to-end: ResearchService → WebSearchProvider → Tavily |

---

## 9. WHAT MUST REMAIN PROVIDER-NEUTRAL

| Component | Provider-Neutral? | Evidence |
|-----------|-------------------|----------|
| `ResearchSource` protocol | YES | Generic `search(query, scope)` |
| `ResearchService` | YES | Consumes any `ResearchSource` |
| Evidence format | YES | `{source, title, content, kind}` — not Tavily-specific |
| `Result` object | YES | Unified contract |
| ServiceContainer registration | YES | `ResearchService([WebSearchProvider()])` |

---

## 10. WHAT BELONGS EXCLUSIVELY INSIDE WEBSEARCHPROVIDER

| Component | Inside WebSearchProvider? |
|-----------|--------------------------|
| Tavily API endpoint URL | YES |
| Tavily API key handling | YES |
| Tavily request construction | YES |
| Tavily response parsing | YES |
| HTTP request execution | YES |
| Timeout handling | YES |
| Tavily-specific error mapping | YES |
| `topic` parameter mapping from `scope` | YES |
| `search_depth` configuration | YES |
| `max_results` configuration | YES |

---

## 11. EXACT FILES TO CREATE/MODIFY

### Files to CREATE

| File | Lines (est.) | Purpose |
|------|-------------|---------|
| `providers/web_search_provider.py` | ~130 | WebSearchProvider implementation |
| `workspace/test_web_search_provider.py` | ~280 | Unit + contract tests |
| `workspace/test_research_integration.py` | ~60 | Integration tests (@integration) |

### Files to MODIFY

| File | Change | Lines |
|------|--------|-------|
| `core/service_container.py` | Add 1 import + 1 registration line | +2 |
| `requirements.txt` | NO CHANGE — `requests` already present | 0 |
| `.env` | Add `TAVILY_API_KEY` (not committed) | +1 |

### Files NOT Modified

| File | Reason |
|------|--------|
| `services/research_service.py` | Protocol unchanged |
| `core/result.py` | Contract unchanged |
| `project_context/PROJECT_STATE.md` | Not yet — after implementation |
| `project_context/CHANGELOG.md` | Not yet — after implementation |

---

## 12. SERVICECONTAINER CHANGE

**YES** — one line change.

```python
# Current (line 110):
self.register("research_service", ResearchService())

# Proposed:
from providers.web_search_provider import WebSearchProvider
# ...
self.register("research_service", ResearchService([WebSearchProvider()]))
```

This is the ONLY ServiceContainer change. ResearchService remains provider-neutral.

---

## 13. REQUIREMENTS.TXT CHANGE

**NO CHANGE.**

Current `requirements.txt` already contains `requests`. No new dependencies needed.

Tavily SDK (`tavily-python`) is NOT required. Raw HTTP POST via `requests` is sufficient and avoids adding a dependency.

---

## 14. ENVIRONMENT VARIABLE

```
TAVILY_API_KEY
```

Format: `tvly-xxxxxxxxxxxxxxxxxxxxx`

Loaded via: `os.getenv("TAVILY_API_KEY")`

---

## 15. ACCEPTANCE CRITERIA FOR OPERATIONALLY VERIFIED

Research Foundation is **OPERATIONALLY VERIFIED** when ALL of the following are true:

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | `python -m compileall providers/web_search_provider.py` | PASS |
| 2 | `pytest workspace/test_web_search_provider.py -v` | ALL PASS (~15 tests) |
| 3 | `pytest workspace/test_research_integration.py -v -m integration` | ALL PASS (~2 tests) |
| 4 | `pytest -m "not integration"` | ALL PASS (no regressions) |
| 5 | `python assistant.py` → user types `research best solar panels` | Returns real evidence |
| 6 | Evidence contains `{source, title, content, kind}` fields | Verified in output |
| 7 | No API key appears in any Result object | Verified in tests |
| 8 | Missing credentials produce clear failure message | Verified in tests |
| 9 | Documentation updated (CHANGELOG, PROJECT_STATE) | PASS |

---

## 16. CLICKBANK COMPATIBILITY

The design remains compatible with future ClickBank ProductSource because:

| Aspect | Research Foundation | ClickBank (Future) |
|--------|--------------------|--------------------|
| Protocol | `ResearchSource` | `ProductSource` (separate) |
| Method | `.search(query, scope)` | `.discover(criteria)` |
| Data model | `{source, title, content, kind}` | `{product_name, gravity, commission, ...}` |
| Service | `ResearchService` | `ProductService` (exists, ranking only) |
| Adapter | `WebSearchProvider` | `ClickBankProvider` (future) |

**They are completely separate bounded contexts.** WebSearchProvider does NOT know about products. ClickBankProvider does NOT know about web search. They can coexist in ServiceContainer without conflict.

---

## PROVIDER COMPARISON

### Tavily vs Brave Search vs Serper vs Scraping

| Criterion | Tavily | Brave Search | Serper | Scraping |
|-----------|--------|-------------|--------|----------|
| Free tier | 1,000/month | $5 credit/month | None | N/A |
| Cost per query | $0.008 (basic) | $0.005 | ~$0.001 | Free (but maintenance) |
| API simplicity | POST JSON | REST | REST | N/A |
| SDK required | NO | NO | NO | N/A |
| Response format | Clean JSON | Clean JSON | Google-like | HTML parsing |
| AI-optimized | YES (purpose-built) | YES (LLM Context) | No | No |
| Legal risk | NONE | NONE | NONE | HIGH |
| Maintenance | LOW | LOW | LOW | HIGH |
| Reliability | HIGH | HIGH | HIGH | LOW |
| Documentation | Excellent | Excellent | Good | N/A |
| **Recommendation** | **SELECTED** | Good alternative | Acceptable | **REJECTED** |

**Tavily wins on:** free tier, simplicity, AI-optimized design, zero SDK dependency.
**Brave is the best alternative** if Tavily becomes unavailable.
**Serper is acceptable** but lacks a free tier.
**Scraping is rejected** for legal, reliability, and maintenance reasons.

---

## DECISION

DECISION:
Tavily

REASON:
Free tier (1,000 credits/month), simple HTTP POST API, AI-optimized response format with title/url/content/score, no SDK required, well-documented OpenAPI spec, purpose-built for agent use cases. Best fit for this project's requirements.

PUBLIC CONTRACT:
`WebSearchProvider.search(query: str, scope: str | None = None) -> Result` — satisfies existing `ResearchSource` protocol exactly.

NORMALIZED RESULT:
`[{source: str, title: str, content: str, kind: "FACT"}]` — direct mapping from Tavily `results[].url`, `results[].title`, `results[].content`.

ENVIRONMENT VARIABLE:
`TAVILY_API_KEY`

IMPLEMENTATION FILES:
- `providers/web_search_provider.py` (NEW, ~130 lines)
- `workspace/test_web_search_provider.py` (NEW, ~280 lines)
- `workspace/test_research_integration.py` (NEW, ~60 lines)
- `core/service_container.py` (MODIFY, +2 lines)

TEST FILES:
- `workspace/test_web_search_provider.py` — unit + contract tests (~18 tests)
- `workspace/test_research_integration.py` — integration tests (~2 tests, @integration)

SERVICECONTAINER CHANGE:
YES — add `WebSearchProvider()` to `ResearchService([WebSearchProvider()])`

CLICKBANK BOUNDARY:
SEPARATE ProductSource — different protocol, different service, different adapter

IMPLEMENTATION AUTHORIZED:
NO — FINAL DESIGN REVIEW ONLY
