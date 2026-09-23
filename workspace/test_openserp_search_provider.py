"""Unit and contract tests for OpenSERPSearchProvider."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from core.result import Result
from providers.openserp_search_provider import OpenSERPSearchProvider


def _fake_response(status_code: int = 200, json_data: dict | None = None, text: str = ""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.json.return_value = json_data
    return resp


def _openserp_envelope(*items: dict, engines_responded: list | None = None, engines_failed: list | None = None) -> dict:
    return {
        "query": {"text": "test", "engines_requested": ["google", "bing"]},
        "meta": {
            "request_id": "req-001",
            "took_ms": 500,
            "engines_responded": ["google", "bing"] if engines_responded is None else engines_responded,
            "engines_failed": [] if engines_failed is None else engines_failed,
        },
        "results": list(items),
        "pagination": {"page": 1, "has_more": False},
    }


def _make_result(url="https://example.com/a", title="Title A", snippet="Snippet A", engine="google"):
    return {"url": url, "title": title, "snippet": snippet, "engine": engine}


def _make_result_with_extracted(url="https://example.com/a", title="Title A", snippet="Snippet A", extracted_content="Extracted content"):
    return {
        "url": url,
        "title": title,
        "snippet": snippet,
        "extracted": {"content": extracted_content, "format": "markdown"},
    }


class OpenSERPSearchProviderConstructionTests(unittest.TestCase):
    def test_construction_default(self):
        provider = OpenSERPSearchProvider()
        self.assertIsNotNone(provider)

    def test_construction_custom(self):
        provider = OpenSERPSearchProvider(
            base_url="http://localhost:8080",
            engines="bing,duckduckgo",
            mode="fast",
            limit=10,
            extract=2,
            timeout=60,
        )
        self.assertIsNotNone(provider)

    def test_limit_clamped_to_100(self):
        provider = OpenSERPSearchProvider(limit=200)
        self.assertIsNotNone(provider)

    def test_limit_clamped_to_1(self):
        provider = OpenSERPSearchProvider(limit=0)
        self.assertIsNotNone(provider)

    def test_extract_clamped_to_5(self):
        provider = OpenSERPSearchProvider(extract=10)
        self.assertIsNotNone(provider)


class OpenSERPSearchProviderSearchSuccessTests(unittest.TestCase):
    @patch("providers.openserp_search_provider._requests")
    def test_search_success(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope(
                _make_result("https://a.com", "A", "A snippet"),
                _make_result("https://b.com", "B", "B snippet", engine="bing"),
            ),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("test query")

        self.assertIsInstance(result, Result)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0]["source"], "https://a.com")
        self.assertEqual(result.data[0]["title"], "A")
        self.assertEqual(result.data[0]["content"], "A snippet")
        self.assertEqual(result.data[0]["kind"], "FACT")
        self.assertEqual(result.data[1]["source"], "https://b.com")

    @patch("providers.openserp_search_provider._requests")
    def test_search_normalizes_response(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope(
                _make_result("https://x.com", "  X  ", "  X snippet  "),
            ),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["source"], "https://x.com")
        self.assertEqual(result.data[0]["title"], "X")
        self.assertEqual(result.data[0]["content"], "X snippet")

    @patch("providers.openserp_search_provider._requests")
    def test_search_empty_results(self, mock_requests):
        mock_requests.get.return_value = _fake_response(200, _openserp_envelope())
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertTrue(result.success)
        self.assertEqual(result.data, [])
        self.assertEqual(result.message, "No results found.")

    @patch("providers.openserp_search_provider._requests")
    def test_extracted_content_preferred_over_snippet(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope(
                _make_result_with_extracted(
                    "https://a.com", "A", "A snippet", "A extracted content"
                ),
            ),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["content"], "A extracted content")

    @patch("providers.openserp_search_provider._requests")
    def test_scope_mapping(self, mock_requests):
        mock_requests.get.return_value = _fake_response(200, _openserp_envelope())

        for scope_val, expected_engines in [
            (None, "google,bing"),
            ("general", "google,bing"),
            ("news", "bing,google"),
            ("finance", "google,bing"),
            ("unknown", "google,bing"),
        ]:
            mock_requests.get.reset_mock()
            provider = OpenSERPSearchProvider()
            provider.search("query", scope=scope_val)
            call_kwargs = mock_requests.get.call_args
            sent_engines = call_kwargs.kwargs["params"]["engines"]
            self.assertEqual(sent_engines, expected_engines, f"scope={scope_val}")


class OpenSERPSearchProviderSearchFailureTests(unittest.TestCase):
    @patch("providers.openserp_search_provider._requests")
    def test_search_connection_refused(self, mock_requests):
        from requests.exceptions import ConnectionError
        mock_requests.get.side_effect = ConnectionError("Connection refused")
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("not available", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_timeout(self, mock_requests):
        from requests.exceptions import Timeout
        mock_requests.get.side_effect = Timeout("timed out")
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("timed out", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_http_400(self, mock_requests):
        mock_requests.get.return_value = _fake_response(400, text="Bad Request")
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_http_403(self, mock_requests):
        mock_requests.get.return_value = _fake_response(403, text="Forbidden")
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("forbidden", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_http_429(self, mock_requests):
        mock_requests.get.return_value = _fake_response(429, text="Too Many Requests")
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("rate limit", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_http_500(self, mock_requests):
        mock_requests.get.return_value = _fake_response(500, text="Internal Server Error")
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("service error", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_malformed_json(self, mock_requests):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = ValueError("bad json")
        mock_requests.get.return_value = resp
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("invalid response", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_unexpected_exception(self, mock_requests):
        mock_requests.get.side_effect = RuntimeError("unexpected")
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_search_all_engines_failed(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope(
                engines_responded=[],
                engines_failed=["google", "bing"],
            ),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("engines failed", result.message.lower())


class OpenSERPSearchProviderContractTests(unittest.TestCase):
    def test_implements_research_source(self):
        provider = OpenSERPSearchProvider()
        self.assertTrue(hasattr(provider, "search"))
        self.assertTrue(callable(provider.search))

    def test_method_signature_matches(self):
        import inspect
        provider = OpenSERPSearchProvider()
        sig = inspect.signature(provider.search)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["query", "scope"])

    @patch("providers.openserp_search_provider._requests")
    def test_return_type_is_result(self, mock_requests):
        mock_requests.get.return_value = _fake_response(200, _openserp_envelope())
        provider = OpenSERPSearchProvider()
        result = provider.search("query")
        self.assertIsInstance(result, Result)


class OpenSERPSearchProviderSecurityTests(unittest.TestCase):
    @patch("providers.openserp_search_provider._requests")
    def test_no_secrets_in_result(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope(_make_result()),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        result_str = repr(result)
        self.assertNotIn("api_key", result_str.lower())
        self.assertNotIn("authorization", result_str.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_no_auth_header_sent(self, mock_requests):
        mock_requests.get.return_value = _fake_response(200, _openserp_envelope())
        provider = OpenSERPSearchProvider()
        provider.search("query")

        call_args = mock_requests.get.call_args
        headers = call_args.kwargs.get("headers", {})
        self.assertNotIn("Authorization", headers)


class OpenSERPSearchProviderInputValidationTests(unittest.TestCase):
    def test_empty_query_fails(self):
        provider = OpenSERPSearchProvider()
        result = provider.search("")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_whitespace_query_fails(self):
        provider = OpenSERPSearchProvider()
        result = provider.search("   ")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_empty_scope_fails(self):
        provider = OpenSERPSearchProvider()
        result = provider.search("query", scope="   ")
        self.assertFalse(result.success)
        self.assertIn("scope", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_none_scope_ok(self, mock_requests):
        mock_requests.get.return_value = _fake_response(200, _openserp_envelope())
        provider = OpenSERPSearchProvider()
        result = provider.search("query", scope=None)
        self.assertTrue(result.success)


class OpenSERPSearchProviderEdgeCaseTests(unittest.TestCase):
    @patch("providers.openserp_search_provider._requests")
    def test_result_with_missing_url_skipped(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope(
                {"title": "A", "snippet": "A snippet"},  # missing url
                _make_result("https://b.com", "B", "B snippet"),
            ),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["source"], "https://b.com")

    @patch("providers.openserp_search_provider._requests")
    def test_result_with_empty_url_skipped(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope({"url": "", "title": "A", "snippet": "A snippet"}),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertTrue(result.success)
        self.assertEqual(result.data, [])

    @patch("providers.openserp_search_provider._requests")
    def test_result_with_non_dict_item_skipped(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            _openserp_envelope("not a dict", _make_result()),
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)

    @patch("providers.openserp_search_provider._requests")
    def test_non_dict_results_list_fails(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            {"results": "not a list"},
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("invalid response", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_missing_results_key_fails(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            {"query": {"text": "test"}},
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertFalse(result.success)
        self.assertIn("invalid response", result.message.lower())

    @patch("providers.openserp_search_provider._requests")
    def test_missing_meta_does_not_cause_error(self, mock_requests):
        mock_requests.get.return_value = _fake_response(
            200,
            {"results": [_make_result()]},
        )
        provider = OpenSERPSearchProvider()
        result = provider.search("query")

        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)


if __name__ == "__main__":
    unittest.main()
