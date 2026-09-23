import unittest
from core.result import Result
from providers.search_browser_adapter import SearchBrowserAdapter


class FakeSearchProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def search(self, query, scope=None):
        self.calls.append((query, scope))
        if self.error:
            raise self.error
        return self.result


class SearchBrowserAdapterTests(unittest.TestCase):
    def test_construction(self):
        adapter = SearchBrowserAdapter(FakeSearchProvider())
        self.assertIsInstance(adapter, SearchBrowserAdapter)

    def test_execute_workflow_delegates_to_search(self):
        provider = FakeSearchProvider(
            Result.ok(data=[{"source": "s", "title": "t", "content": "c", "kind": "FACT"}])
        )
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("execute_workflow", "python affiliate")
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "python affiliate")

    def test_extract_operation_delegates_to_search(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", "test query")
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "test query")

    def test_inspect_operation_delegates_to_search(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("inspect", "test query")
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "test query")

    def test_unsupported_operation_fails(self):
        adapter = SearchBrowserAdapter(FakeSearchProvider())
        result = adapter.execute("navigate", "https://example.test")
        self.assertFalse(result.success)
        self.assertIn("not supported", result.message.lower())

    def test_dict_payload_extracts_query(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", {"query": "test", "scope": "news"})
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "test")
        self.assertEqual(provider.calls[0][1], "news")

    def test_dict_payload_text_key(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", {"text": "from_text"})
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "from_text")

    def test_list_payload_extracts_first_string(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", ["list query"])
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "list query")

    def test_list_payload_extracts_first_dict(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", [{"query": "dict query"}])
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "dict query")

    def test_empty_string_payload_fails(self):
        adapter = SearchBrowserAdapter(FakeSearchProvider())
        result = adapter.execute("extract", "")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_none_payload_fails(self):
        adapter = SearchBrowserAdapter(FakeSearchProvider())
        result = adapter.execute("extract", None)
        self.assertFalse(result.success)

    def test_non_string_operation_fails(self):
        adapter = SearchBrowserAdapter(FakeSearchProvider())
        result = adapter.execute(123, "query")
        self.assertFalse(result.success)

    def test_provider_failure_normalized(self):
        provider = FakeSearchProvider(Result.fail("provider error"))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", "query")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "provider error")

    def test_provider_exception_normalized(self):
        provider = FakeSearchProvider(error=RuntimeError("boom"))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", "query")
        self.assertFalse(result.success)
        self.assertIn("failed", result.message.lower())

    def test_provider_returns_non_result_fails(self):
        provider = FakeSearchProvider(result="not_a_result")
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", "query")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_provider_without_search_method_fails(self):
        adapter = SearchBrowserAdapter("not_a_provider")
        result = adapter.execute("extract", "query")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_search_result_data_forwarded(self):
        evidence = [
            {"source": "url", "title": "Title", "content": "Body", "kind": "FACT"},
        ]
        provider = FakeSearchProvider(Result.ok(data=evidence))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("execute_workflow", "query")
        self.assertTrue(result.success)
        self.assertEqual(result.data, evidence)

    def test_whitespace_query_stripped(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        result = adapter.execute("extract", "  spaced  ")
        self.assertTrue(result.success)
        self.assertEqual(provider.calls[0][0], "spaced")

    def test_scope_forwarded_from_dict(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        adapter.execute("extract", {"query": "q", "scope": "finance"})
        self.assertEqual(provider.calls[0][1], "finance")

    def test_scope_none_for_string_payload(self):
        provider = FakeSearchProvider(Result.ok(data=[]))
        adapter = SearchBrowserAdapter(provider)
        adapter.execute("extract", "query")
        self.assertIsNone(provider.calls[0][1])


if __name__ == "__main__":
    unittest.main()
