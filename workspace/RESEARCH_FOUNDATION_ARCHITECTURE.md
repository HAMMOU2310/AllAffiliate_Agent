# RESEARCH FOUNDATION ARCHITECTURE — AllAffiliate_Agent

**Design Date:** 2026-08-30
**Architect:** Research Foundation Architect
**Baseline:** v1.0 commit `b72d93d`
**Task Type:** DESIGN-ONLY — No files created, no contracts modified

> **UPDATE (2026-09-01):** This design document originally proposed Tavily as the first WebSearchProvider.
> The implementation has been superseded by **OpenSERP OSS** (`providers/openserp_search_provider.py`).
> OpenSERP is self-hosted, MIT-licensed, requires no API key, and supports multiple search engines.
> The `ResearchSource` protocol and evidence contract remain unchanged.

---

## 1. CURRENT RESEARCH CONTRACT

### Exact Public Protocol

```python
# services/research_service.py — lines 11-15

class ResearchSource(Protocol):
    """Minimal source boundary consumed by ResearchService."""

    def search(self, query: str, scope: str | None = None) -> Result:
        ...
```

### Method Signature Analysis

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| `self` | ResearchSource | — | Protocol boundary |
| `query` | `str` | YES | Non-empty string enforced by ResearchService before calling |
| `scope` | `str \| None` | NO | If provided, must be non-empty string |

### Return Contract

The `search()` method MUST return a `Result` object.

**On success:**
```python
Result.ok(
    data=[
        {
            "source": str,   # required, non-empty
            "title": str,    # required, non-empty
            "content": str,  # required, non-empty
            "kind": str,     # required, must be "FACT" (case-insensitive)
        },
        ...
    ]
)
```

**On failure:**
```python
Result.fail(message="descriptive error message")
```

### Evidence Normalization Rules (ResearchService._normalize_evidence)

1. `data` must be a list (not str, bytes, Mapping)
2. Each item must be a Mapping
3. Each item must have all 4 keys: `source`, `title`, `content`, `kind`
4. All 4 values must be non-empty strings
5. `kind` must equal `"FACT"` (case-insensitive, normalized to uppercase)
6. Return value is normalized to `{"source", "title", "content", "kind": "FACT"}`

### Current Dependency Injection

```python
# core/service_container.py — line 110
self.register("research_service", ResearchService())
```

ResearchService is registered with **no sources** (empty tuple). Any call to `research()` returns:
```python
Result.fail("No research source is registered.")
```

### Current Failure Behavior

| Scenario | Behavior |
|----------|----------|
| Empty query | `Result.fail("Research query is invalid.")` |
| Invalid scope | `Result.fail("Research scope is invalid.")` |
| No sources | `Result.fail("No research source is registered.")` |
| Source raises exception | `Result.fail("Research source execution failed.")` — exception details NOT exposed |
| Source returns non-Result | `Result.fail("Research source returned an invalid Result.")` |
| Source returns failure | `Result.fail("Research source failed.")` |
| Evidence malformed | `Result.fail("Research source returned malformed evidence.")` |
| Non-FACT kind | `Result.fail("Research source returned malformed evidence.")` |

**Critical observation:** ResearchService is fail-closed. ANY source failure stops ALL research. There is no partial aggregation.

### Current Test Coverage

| Test | Type | What It Proves |
|------|------|----------------|
| `test_construction_without_sources` | Unit | Service constructs without sources |
| `test_success_normalizes_fact_evidence` | Unit | Evidence normalization works |
| `test_invalid_query_and_scope_fail` | Unit | Input validation works |
| `test_missing_source_fails` | Unit | No-source failure works |
| `test_source_failure_is_normalized` | Unit | Exception handling works, secrets not leaked |
| `test_malformed_evidence_fails` | Unit | Malformed data rejection works |
| `test_non_fact_evidence_is_rejected` | Unit | Kind validation works |

**Total:** 7 tests, all using `FakeSource` mock. No real API tests.

### Current Runtime Status

**NO operational research capability.** The service exists but has no registered sources. Any research command fails immediately.

---

## 2. RESEARCH FOUNDATION RESPONSIBILITY

### What Research Foundation Should Provide

Research Foundation is the **data acquisition layer**. It answers: "What information exists about this topic?"

It must NOT:
- Analyze or classify information (AnalysisService)
- Plan workflows (WorkflowService)
- Generate content (ContentService)
- Make policy decisions (PolicyService)
- Publish anything (PublishingService)

### Responsibility Decomposition

| Responsibility | Owner | WebSearchProvider Role |
|----------------|-------|----------------------|
| **A. Search execution** | WebSearchProvider | Execute API call, handle credentials, manage connection |
| **B. Result normalization** | WebSearchProvider | Convert API response to `list[dict]` with required fields |
| **C. Source metadata** | WebSearchProvider | Populate `source` (URL), `title`, `content` (snippet), `kind` ("FACT") |
| **D. Content extraction** | WebSearchProvider | Extract meaningful text from API response |
| **E. Reliability/error handling** | WebSearchProvider | Handle timeouts, DNS, API errors, rate limits |
| **F. Deduplication** | ResearchService | NOT WebSearchProvider — dedup across multiple sources |
| **G. Optional ranking** | Future component | NOT WebSearchProvider — ranking is analysis, not search |

### Minimum WebSearchProvider Responsibility

WebSearchProvider does ONE thing: **translate a search query into an API call and normalize the response.**

```
Input:  query (str), scope (str|None)
Output: Result.ok(data=[{source, title, content, kind}, ...])
        or Result.fail(message)
```

Everything else (deduplication, ranking, cross-source aggregation, analysis) stays in ResearchService or downstream services.

---

## 3. WEB SEARCH PROVIDER OPTIONS

### Option A: Generic HTTP/Search API Adapter

| Attribute | Assessment |
|-----------|------------|
| Example | Custom adapter using `requests` to call any search API |
| Stability | HIGH — adapter controls request/response format |
| Legality | COMPLIANT — uses official APIs |
| Reliability | HIGH — standard HTTP with proper error handling |
| Cost | VARIABLE — depends on chosen API |
| Rate limits | MANAGEABLE — standard API rate limiting |
| Anti-bot risk | NONE — official API calls |
| Testability | HIGH — fake HTTP responses in tests |
| Maintenance | LOW — simple request/response translation |
| Credentials | API key via environment variable |
| Architecture fit | EXCELLENT — follows GeminiProvider pattern exactly |

### Option B: Dedicated Search API Provider (SerpAPI, Tavily, Exa)

| Attribute | Assessment |
|-----------|------------|
| Example | SerpAPI, Tavily Search API, Exa API |
| Stability | HIGH — established providers |
| Legality | COMPLIANT — official APIs |
| Reliability | HIGH — managed infrastructure |
| Cost | LOW-MEDIUM — free tiers available |
| Rate limits | STANDARD — tier-based |
| Anti-bot risk | NONE — official API |
| Testability | HIGH — mock API responses |
| Maintenance | LOW — SDK handles complexity |
| Credentials | API key via environment variable |
| Architecture fit | GOOD — but adds SDK dependency |

### Option C: Search Engine SDK

| Attribute | Assessment |
|-----------|------------|
| Example | `google-search-results` (SerpAPI SDK) |
| Stability | DEPENDS on SDK maintenance |
| Legality | COMPLIANT |
| Reliability | MEDIUM — SDK adds failure surface |
| Cost | SAME as Option B |
| Rate limits | SAME as Option B |
| Anti-bot risk | NONE |
| Testability | MEDIUM — harder to mock SDK internals |
| Maintenance | MEDIUM — SDK version updates required |
| Credentials | API key via environment variable |
| Architecture fit | ACCEPTABLE — but adds unnecessary abstraction |

### Option D: Direct Web Scraping

| Attribute | Assessment |
|-----------|------------|
| Example | BeautifulSoup, Playwright, Selenium |
| Stability | LOW — HTML structure changes break scrapers |
| Legality | RISKY — may violate ToS |
| Reliability | LOW — anti-bot measures, CAPTCHAs |
| Cost | HIGH — maintenance overhead |
| Rate limits | SEVERE — IP blocking, bans |
| Anti-bot risk | HIGH — primary concern |
| Testability | LOW — hard to test without real sites |
| Maintenance | HIGH — constant breakage |
| Credentials | None (but proxy costs) |
| Architecture fit | POOR — violates provider-neutral principle |

### Evaluation Matrix

| Criterion | Weight | Option A | Option B | Option C | Option D |
|-----------|--------|----------|----------|----------|----------|
| Stability | 20% | 9 | 9 | 7 | 3 |
| Legality | 15% | 10 | 10 | 10 | 4 |
| Reliability | 20% | 9 | 9 | 7 | 3 |
| Cost | 10% | 8 | 7 | 7 | 6 |
| Testability | 15% | 9 | 9 | 7 | 3 |
| Maintenance | 10% | 8 | 8 | 6 | 3 |
| Architecture fit | 10% | 10 | 8 | 7 | 4 |
| **Weighted Score** | | **9.05** | **8.85** | **7.35** | **3.55** |

**Winner: Option A (Generic HTTP/Search API Adapter)**

---

## 4. SELECTED APPROACH

### DECISION

**Option A: Generic HTTP/Search API Adapter**

A single `WebSearchProvider` class that:
1. Accepts an HTTP-based search API configuration (endpoint, parameters, response mapping)
2. Translates `query` and `scope` into API request parameters
3. Makes HTTP request using `requests` (already in requirements.txt)
4. Normalizes response into the required evidence format
5. Returns `Result.ok(data=[...])` or `Result.fail(message)`

### WHY

1. **Follows established patterns:** Matches GeminiProvider exactly — lazy client, `os.getenv()` for credentials, response normalization, fail-closed error handling
2. **Provider-neutral:** The adapter doesn't hardcode any specific search API. Configuration determines which API is called.
3. **Minimal dependencies:** Uses `requests` (already in requirements.txt). No new packages.
4. **Testable:** Fake HTTP responses in unit tests, real API calls in integration tests
5. **Extensible:** Future adapters (Bing, Exa, Tavily) can be added as separate classes or configuration variants
6. **Architecture fit:** All external SDK/API objects stay inside the provider boundary

### ALTERNATIVES REJECTED

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Option B (Dedicated API) | Adds unnecessary SDK dependency; Option A achieves the same with less coupling |
| Option C (SDK) | Harder to mock, adds version management, less control over error handling |
| Option D (Scraping) | Legally risky, unreliable, high maintenance, violates provider-neutral principle |

---

## 5. DATA CONTRACTS

### ResearchQuery (Input)

```python
@dataclass(frozen=True, slots=True)
class ResearchQuery:
    query: str          # required, non-empty
    scope: str | None   # optional, non-empty if provided
```

**Validation:** Already handled by ResearchService before calling source.search().

### ResearchResult (Output from WebSearchProvider.search)

```python
# Returned as Result.ok(data=[...])
# Each item is a dict with exactly these keys:

{
    "source": str,    # URL or identifier of the source
    "title": str,     # Title of the result
    "content": str,   # Snippet or extracted text
    "kind": str,      # Always "FACT"
}
```

**Why this exact shape:**
- Matches `ResearchService._normalize_evidence()` requirements exactly
- `source` = URL allows deduplication by URL
- `title` = result title enables content relevance assessment
- `content` = snippet provides the actual information
- `kind` = "FACT" is the only accepted kind (ResearchService enforces this)

### SourceMetadata (Internal to WebSearchProvider)

```python
# NOT exposed outside the provider boundary
# Used internally for response normalization

{
    "raw_url": str,
    "raw_title": str,
    "raw_snippet": str,
    "raw_position": int,
    "raw_score": float | None,
}
```

### Deduplication Identity

Research results are deduplicated by:
1. `source` (URL) — primary dedup key
2. `title` — secondary dedup key (same URL, different title = keep both)

Deduplication happens in **ResearchService**, not WebSearchProvider.

### Serialization

All evidence dicts are JSON-serializable. No custom types, no datetime objects, no binary data.

### Secret-Sensitive Fields

The following must NEVER appear in Result.data, Result.errors, or Result.metadata:
- API keys
- Authentication tokens
- Request headers with credentials
- Full request URLs with embedded credentials

---

## 6. WEBSEARCHPROVIDER CONTRACT

### Constructor

```python
class WebSearchProvider:
    def __init__(
        self,
        endpoint: str | None = None,       # API endpoint URL
        api_key_env: str = "WEBSEARCH_API_KEY",  # env var name for API key
        request_config: dict | None = None, # provider-specific request params
        result_mapping: dict | None = None, # field mapping from API response
        timeout: int = 30,                  # request timeout in seconds
        max_results: int = 10,              # maximum results to return
    ) -> None:
        ...
```

### Required Public Method

```python
def search(self, query: str, scope: str | None = None) -> Result:
    """Execute a web search and return normalized evidence."""
    ...
```

This method satisfies the `ResearchSource` protocol exactly.

### Request Translation

```
User query → WebSearchProvider.search(query, scope)
    ↓
Construct HTTP request:
    - endpoint: self._endpoint
    - params: self._build_params(query, scope)
    - headers: {"Authorization": f"Bearer {api_key}"} (if applicable)
    ↓
Execute via requests.get()
    ↓
Parse response → normalize to evidence list
```

### Credential Handling

```python
api_key = os.getenv(self._api_key_env)
if not api_key or not api_key.strip():
    return Result.fail("Web search credentials are not configured.")
```

- Credentials loaded from environment variable
- Variable name is configurable (default: `WEBSEARCH_API_KEY`)
- Never logged, never in Result.data, never in Result.errors
- Lazy loading: client created on first search, reused for subsequent calls

### Response Normalization

```python
def _normalize_response(self, raw_response: dict) -> list[dict[str, str]]:
    """Convert API response to evidence list."""
    results = []
    for item in raw_response.get("results", []):
        evidence = {
            "source": str(item.get("url", "")),
            "title": str(item.get("title", "")),
            "content": str(item.get("snippet", "")),
            "kind": "FACT",
        }
        # Validate all fields are non-empty
        if all(evidence[k].strip() for k in ("source", "title", "content")):
            results.append(evidence)
    return results
```

### Timeout

Default: 30 seconds. Configurable via constructor.

### Retry Policy

**No automatic retries.** Reasons:
1. ResearchService is fail-closed — a failed source stops all research
2. Retries on transient failures may be appropriate, but the caller (ResearchService) should decide
3. WebSearchProvider reports the failure; ResearchService can decide to retry or fail

Future enhancement: ResearchService could implement retry logic with backoff.

### Rate Limiting

**No built-in rate limiting.** WebSearchProvider makes one request per `search()` call.

Rate limiting should be handled by:
1. The API provider (their infrastructure)
2. The caller (ResearchService can throttle if needed)

### Malformed Response Handling

```python
try:
    raw_response = response.json()
except (ValueError, TypeError):
    return Result.fail("Web search returned an invalid response.")
```

### Empty Result Handling

```python
evidence = self._normalize_response(raw_response)
if not evidence:
    return Result.ok(data=[], message="No results found.")
```

Empty results are NOT failures. They are valid outcomes.

### Provider Failure Handling

| Failure Type | Response |
|--------------|----------|
| Missing credentials | `Result.fail("Web search credentials are not configured.")` |
| Invalid credentials | `Result.fail("Web search authentication failed.")` |
| Network timeout | `Result.fail("Web search request timed out.")` |
| DNS failure | `Result.fail("Web search request failed.")` |
| HTTP 4xx | `Result.fail("Web search request failed.")` |
| HTTP 5xx | `Result.fail("Web search request failed.")` |
| Rate limit (429) | `Result.fail("Web search rate limit exceeded.")` |
| Malformed response | `Result.fail("Web search returned an invalid response.")` |
| Empty response | `Result.ok(data=[])` — not a failure |
| Unexpected exception | `Result.fail("Web search execution failed.")` |

---

## 7. SERVICE BOUNDARY

### Architecture Diagram

```
ResearchService (provider-neutral)
    │
    │  .research(query, scope)
    │
    ├── ResearchSource Protocol
    │       │
    │       │  .search(query, scope) -> Result
    │       │
    │       └── WebSearchProvider (concrete)
    │               │
    │               │  requests.get(endpoint, ...)
    │               │
    │               └── External Search API
    │                       (SerpAPI, Bing, Exa, etc.)
    │
    └── [Future] ProductSourceProvider (ClickBank-specific)
            │
            │  .search(query, scope) -> Result
            │
            └── ClickBank API
```

### What ResearchService Knows

- The `ResearchSource` protocol (search method signature)
- That sources return `Result` objects
- That evidence must have `{source, title, content, kind}` fields
- That `kind` must be "FACT"

### What ResearchService Does NOT Know

- SDK request objects
- API-specific exceptions
- API-specific response objects
- Vendor-specific authentication
- Vendor-specific pagination
- HTTP request details
- API endpoint URLs
- API key variable names

### What WebSearchProvider Knows

- Its own API endpoint and authentication method
- How to translate query/scope into API parameters
- How to parse its specific API response format
- How to normalize response into evidence format

### What WebSearchProvider Does NOT Know

- That ResearchService exists
- That other sources exist
- How evidence will be used downstream
- Any analysis, ranking, or publishing logic

---

## 8. SECURITY MODEL

### Credential Flow

```
.env file (not committed)
    ↓
os.getenv("WEBSEARCH_API_KEY")
    ↓
WebSearchProvider.__init__() stores env var name
    ↓
WebSearchProvider.search() loads key at call time
    ↓
requests.get() sends key in Authorization header
    ↓
Key is NEVER stored in Result objects
```

### Security Rules

1. **Environment variables only:** API keys loaded from `os.getenv()`
2. **No hardcoding:** No API keys in source code
3. **No logging:** API keys never logged (even in debug mode)
4. **No Result exposure:** Keys never appear in Result.data, Result.errors, or Result.metadata
5. **No Git commit:** `.env` is in `.gitignore`
6. **Lazy loading:** Key loaded only when search is called, not at construction
7. **Error sanitization:** Authentication failures return generic messages, not key details

### Test Security

Tests use `unittest.mock.patch.dict(os.environ, ...)` to set test credentials. Real credentials are never used in tests.

---

## 9. FAILURE MODEL

### Fail-Closed Policy

WebSearchProvider follows the project's fail-closed principle:
- Any failure returns `Result.fail(message)`
- No partial results on failure
- No silent failures
- No swallowed exceptions

### Failure Categories

| Category | Example | Retry Safe? | Action |
|----------|---------|-------------|--------|
| Missing credentials | No API key | NO | Fail immediately |
| Invalid credentials | Wrong API key | NO | Fail immediately |
| Network timeout | Server too slow | YES (once) | Report failure |
| DNS failure | Invalid endpoint | NO | Fail immediately |
| API failure (4xx) | Bad request | NO | Fail immediately |
| API failure (5xx) | Server error | MAYBE (once) | Report failure |
| Rate limit (429) | Too many requests | NO (wait needed) | Report failure |
| Malformed response | Unexpected format | NO | Fail immediately |
| Empty result | No results found | N/A | Return empty list |
| Provider unavailable | Service down | NO | Fail immediately |
| Unexpected exception | Bug in code | NO | Fail immediately |

### Retry Safety

Retries are NOT implemented in WebSearchProvider because:
1. The caller (ResearchService) owns the orchestration decision
2. Some failures are not idempotent (rate limits need backoff)
3. Fail-closed behavior means any failure stops the pipeline
4. Retries add complexity without clear benefit at this stage

**Future enhancement:** ResearchService could implement retry with exponential backoff for transient failures (5xx, timeouts).

---

## 10. RESEARCH QUALITY MODEL

### Minimum Source Quality Metadata

Every evidence record MUST have:

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `source` | YES | URL or identifier | `"https://example.com/article"` |
| `title` | YES | Result title | `"Best Solar Panels 2026"` |
| `content` | YES | Snippet or extracted text | `"Solar panels reduce energy costs by..."` |
| `kind` | YES | Always `"FACT"` | `"FACT"` |

### Optional Enhancement Fields (Future)

These fields could be added without breaking the existing contract:

| Field | Description | When to Add |
|-------|-------------|-------------|
| `domain` | Extracted domain | When dedup by domain is needed |
| `published_date` | Publication date | When recency ranking is needed |
| `retrieved_at` | When the result was fetched | When freshness tracking is needed |
| `confidence` | Relevance score | When quality ranking is needed |
| `source_type` | "web", "api", "news" | When source filtering is needed |

**Decision:** Do NOT add these fields now. The current 4-field contract is sufficient. Fields can be added later as optional additions to the evidence dict without breaking ResearchService.

### Auditability

Every research result is auditable because:
1. `source` provides the origin URL
2. `title` identifies the specific content
3. `content` contains the actual information
4. ResearchService metadata includes `query`, `source_count`, `evidence_count`
5. Result objects are immutable (frozen dataclass)

---

## 11. TEST ARCHITECTURE

### Test Categories

| Category | Marker | Count | Purpose |
|----------|--------|-------|---------|
| Unit tests | None (default) | ~15 | Test provider logic with fake HTTP |
| Contract tests | None | ~3 | Test ResearchSource protocol compliance |
| Integration tests | `@pytest.mark.integration` | 1-2 | Real API call to search provider |
| Real smoke tests | `@pytest.mark.integration` | 1 | End-to-end: user query → real results |

### Unit Tests (No External Dependencies)

```
test_websearch_provider.py:
  - test_construction_default
  - test_construction_custom_config
  - test_search_success
  - test_search_normalizes_response
  - test_search_empty_results
  - test_search_missing_credentials
  - test_search_invalid_credentials (401)
  - test_search_network_timeout
  - test_search_dns_failure
  - test_search_api_failure (500)
  - test_search_rate_limit (429)
  - test_search_malformed_response
  - test_search_unexpected_exception
  - test_search_result_compatibility
  - test_search_source_protocol_compliance
  - test_secret_not_in_result
```

### Contract Tests

```
test_research_source_contract.py:
  - test_websearchprovider_implements_research_source
  - test_search_method_signature_matches_protocol
  - test_return_type_is_result
```

### Integration Tests

```
test_research_integration.py:
  - test_real_search_returns_evidence (requires WEBSEARCH_API_KEY)
  - test_research_service_with_websearchprovider (end-to-end)
```

### Test Fixtures

```python
class FakeHTTPResponse:
    """Simulates requests.Response for unit tests."""
    def __init__(self, json_data=None, status_code=200, text=""):
        self._json = json_data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._json

class FakeRequests:
    """Simulates requests module for unit tests."""
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        if self._error:
            raise self._error
        return self._response
```

### Credential Isolation

```python
def test_search_missing_credentials():
    with unittest.mock.patch.dict(os.environ, {}, clear=True):
        provider = WebSearchProvider()
        result = provider.search("test query")
        assert not result.success
        assert "credentials" in result.message.lower()
```

### Normal pytest Must Not Require Credentials

```bash
# All unit and contract tests pass without any credentials
pytest workspace/test_websearch_provider.py -v

# Integration tests require credentials and are skipped by default
pytest workspace/test_research_integration.py -v -m integration
```

---

## 12. CLICKBANK SEPARATION

### Architecture

```
ResearchService
    │
    ├── [Future] WebSearchProvider
    │       Purpose: General web search
    │       Input: Any query
    │       Output: Web search results
    │
    └── [Future] ClickBankProvider
            Purpose: ClickBank product/offer discovery
            Input: ClickBank-specific parameters (gravity, commission, category)
            Output: ClickBank product data
            Note: Implements a DIFFERENT protocol, NOT ResearchSource
```

### Why ClickBank Is Separate

1. **Different data model:** ClickBank products have gravity, commission %, refund rate, etc. Web search results have URL, title, snippet.
2. **Different query model:** ClickBank queries are category/gravity/commission filters. Web queries are natural language.
3. **Different use case:** Product discovery vs. information gathering.
4. **Different API:** ClickBank API vs. search API.

### Future ClickBank Protocol

```python
class ProductSource(Protocol):
    """Protocol for product/offer discovery sources."""
    def discover(self, criteria: dict[str, Any]) -> Result:
        ...
```

This is a SEPARATE protocol from ResearchSource. ClickBankProvider implements ProductSource, NOT ResearchSource.

### Coexistence

ResearchService and ProductService are separate services:
- `ResearchService` uses `ResearchSource` → web information
- `ProductService` (future) uses `ProductSource` → product data

They can be called independently or composed in a workflow.

---

## 13. FUTURE CONTENT PIPELINE

### How Research Foundation Supports the Full Pipeline

```
User Goal: "Write an article about the best solar panels"
    │
    ├── ResearchService.research("best solar panels 2026")
    │     └── WebSearchProvider.search("best solar panels 2026")
    │           → [{source, title, content, kind: "FACT"}, ...]
    │
    ├── AnalysisService.analyze(evidence, question="What are the best solar panels?")
    │     → [{kind: "FACT", content: ...}, {kind: "RECOMMENDATION", content: ...}]
    │
    ├── WorkflowService.plan("Write article about solar panels", context={evidence, analysis})
    │     → [{id: "1", description: "Draft introduction", status: "PENDING"}, ...]
    │
    ├── ContentService.create(brief, persona, format="blog post")
    │     → {title: "...", body: "...", claims: [...]}
    │
    └── PublishingService.publish(asset, destination="blog")
          → Result.ok(...)
```

### No Contract Changes Required

The existing contracts already support this pipeline:
- `ResearchSource.search()` returns evidence
- `AnalysisService.analyze()` accepts evidence
- `WorkflowService.plan()` accepts goal + context
- `ContentService.create()` accepts brief + persona
- `PublishingService.publish()` accepts asset + destination

The only missing piece is the concrete `WebSearchProvider` implementing `ResearchSource`.

---

## 14. PROPOSED FILE STRUCTURE

```
AllAffiliate_Agent/
├── providers/
│   ├── openai_provider.py              # existing
│   ├── gemini_provider.py              # existing
│   ├── cloud_ai_content_generator.py   # existing
│   └── web_search_provider.py          # NEW — WebSearchProvider
│
├── services/
│   ├── research_service.py             # existing — NO CHANGES
│   ├── analysis_service.py             # existing — NO CHANGES
│   ├── workflow_service.py             # existing — NO CHANGES
│   └── content_service.py              # existing — NO CHANGES
│
├── workspace/
│   ├── test_web_search_provider.py     # NEW — unit tests (~15 tests)
│   ├── test_research_source_contract.py # NEW — contract tests (~3 tests)
│   ├── test_research_integration.py    # NEW — integration tests (~2 tests, @integration)
│   └── test_research_service.py        # existing — NO CHANGES
│
├── core/
│   ├── result.py                       # existing — NO CHANGES
│   └── service_container.py            # existing — MODIFIED (register WebSearchProvider)
│
├── conftest.py                         # existing — add "research" marker if needed
│
└── .env                                # add WEBSEARCH_API_KEY
```

### File Responsibilities

| File | Lines (est.) | Purpose |
|------|-------------|---------|
| `providers/web_search_provider.py` | ~120 | Search API adapter |
| `workspace/test_web_search_provider.py` | ~250 | Unit tests |
| `workspace/test_research_source_contract.py` | ~50 | Contract compliance tests |
| `workspace/test_research_integration.py` | ~60 | Real API integration tests |

### Why This Structure

- **Follows existing conventions:** providers/ for adapters, workspace/ for tests
- **Minimal changes:** Only 1 new production file, 3 new test files
- **No contract changes:** ResearchSource protocol unchanged
- **No service changes:** ResearchService unchanged
- **ServiceContainer change:** Only 1 line added to register WebSearchProvider

---

## 15. IMPLEMENTATION PLAN

### Stage 0 — Contract Verification

| Attribute | Value |
|-----------|-------|
| Files | None |
| Dependency | None |
| Acceptance | Verify ResearchSource protocol is sufficient for WebSearchProvider |
| Failure | If protocol is insufficient, design changes needed (unlikely) |

### Stage 1 — Provider Skeleton

| Attribute | Value |
|-----------|-------|
| Files | `providers/web_search_provider.py` |
| Dependency | Stage 0 |
| Acceptance | Class constructs, `search()` method exists, satisfies ResearchSource |
| Failure | If constructor design is wrong |

### Stage 2 — Request/Response Normalization

| Attribute | Value |
|-----------|-------|
| Files | `providers/web_search_provider.py` |
| Dependency | Stage 1 |
| Acceptance | Query → HTTP request, response → evidence list |
| Failure | If API response parsing fails |

### Stage 3 — Credential Handling

| Attribute | Value |
|-----------|-------|
| Files | `providers/web_search_provider.py` |
| Dependency | Stage 2 |
| Acceptance | Credentials from env, missing credentials fail gracefully |
| Failure | If credential handling is insecure |

### Stage 4 — Error Handling

| Attribute | Value |
|-----------|-------|
| Files | `providers/web_search_provider.py` |
| Dependency | Stage 3 |
| Acceptance | All failure modes produce Result.fail with appropriate messages |
| Failure | If any exception escapes |

### Stage 5 — Unit Tests

| Attribute | Value |
|-----------|-------|
| Files | `workspace/test_web_search_provider.py` |
| Dependency | Stage 4 |
| Acceptance | All unit tests pass, no credentials needed |
| Failure | If any test fails |

### Stage 6 — ResearchService Integration

| Attribute | Value |
|-----------|-------|
| Files | `core/service_container.py` |
| Dependency | Stage 5 |
| Acceptance | WebSearchProvider registered in ServiceContainer, ResearchService receives it |
| Failure | If integration breaks existing tests |

### Stage 7 — Real Smoke Test

| Attribute | Value |
|-----------|-------|
| Files | `workspace/test_research_integration.py` |
| Dependency | Stage 6 |
| Acceptance | Real API call returns evidence, full pipeline works |
| Failure | If API is unreachable or credentials are wrong |

### Stage 8 — Operational Verification

| Attribute | Value |
|-----------|-------|
| Files | None |
| Dependency | Stage 7 |
| Acceptance | User can run `python assistant.py` and execute a research command |
| Failure | If end-to-end flow breaks |

### Stage 9 — Documentation

| Attribute | Value |
|-----------|-------|
| Files | `project_context/CHANGELOG.md`, `project_context/PROJECT_STATE.md` |
| Dependency | Stage 8 |
| Acceptance | Research Foundation documented as operational |
| Failure | If documentation is inaccurate |

---

## 16. ARCHITECTURAL DECISION

### DECISION

**Generic HTTP/Search API Adapter (Option A)** — A single `WebSearchProvider` class that makes HTTP requests to any search API and normalizes responses.

### WHY

1. **Follows established patterns:** Matches GeminiProvider exactly
2. **Provider-neutral:** No hardcoded API; configuration determines behavior
3. **Minimal dependencies:** Uses `requests` (already required)
4. **Testable:** Fake HTTP responses in unit tests
5. **Extensible:** Future adapters are separate classes
6. **Architecture fit:** All external objects stay inside provider boundary

### ALTERNATIVES REJECTED

| Alternative | Reason |
|-------------|--------|
| SerpAPI SDK | Adds unnecessary dependency; Option A achieves same with less coupling |
| Tavily SDK | Same as above |
| Direct scraping | Legally risky, unreliable, high maintenance |
| Bing SDK | Same as SerpAPI SDK |

---

## 17. RISKS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Search API changes response format | MEDIUM | HIGH | Response normalization is centralized; update one function |
| API key compromised | LOW | HIGH | Environment variables only; never in logs or Results |
| Rate limiting blocks research | MEDIUM | MEDIUM | Exponential backoff in future; current fail-closed is safe |
| API provider goes offline | LOW | HIGH | Provider-neutral design allows switching APIs |
| Search results are low quality | MEDIUM | MEDIUM | Quality is AnalysisService concern, not WebSearchProvider |
| New API requires SDK | LOW | MEDIUM | Create new adapter class; existing one stays |

---

## 18. FINAL RECOMMENDATION

### CURRENT RESEARCH STATUS:
**NO operational research capability.** ResearchService exists with clean contracts but has no registered sources. Any research command fails immediately with "No research source is registered."

### WEBSEARCHPROVIDER:
**PROPOSED** — Generic HTTP/search API adapter implementing ResearchSource protocol. Follows GeminiProvider pattern. Uses `requests` library. ~120 lines of production code.

### CLICKBANK:
**SEPARATE FUTURE ADAPTER** — ClickBank product discovery will use a separate `ProductSource` protocol and `ClickBankProvider` class. It will NOT extend or modify WebSearchProvider.

### NEW PRODUCTION CODE:
**1 file:** `providers/web_search_provider.py` (~120 lines)

### CONTRACTS MODIFIED:
**NONE** — ResearchSource protocol unchanged, ResearchService unchanged

### ARCHITECTURE MODIFIED:
**NONE** — Only ServiceContainer registration changes (1 line)

### IMPLEMENTATION AUTHORIZED:
**NO — DESIGN ONLY**
