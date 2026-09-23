import unittest

from core.result import Result
from services.research_service import ResearchService


class FakeSource:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def search(self, query, scope=None):
        self.calls.append((query, scope))
        if self.error is not None:
            raise self.error
        return self.result


class ResearchServiceTests(unittest.TestCase):
    def test_construction_without_sources(self):
        self.assertIsInstance(ResearchService(), ResearchService)

    def test_success_normalizes_fact_evidence(self):
        source = FakeSource(
            Result.ok(
                data=[
                    {
                        "source": "catalog",
                        "title": "Product",
                        "content": "Observed description",
                        "kind": "fact",
                    }
                ]
            )
        )

        result = ResearchService([source]).research("product", scope="market")

        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["kind"], "FACT")
        self.assertEqual(result.metadata["evidence_count"], 1)
        self.assertEqual(source.calls, [("product", "market")])

    def test_invalid_query_and_scope_fail(self):
        service = ResearchService()
        self.assertFalse(service.research("").success)
        self.assertFalse(service.research("topic", scope=" ").success)

    def test_missing_source_fails(self):
        result = ResearchService().research("topic")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No research source is registered.")

    def test_source_failure_is_normalized(self):
        source = FakeSource(error=RuntimeError("private source detail"))
        result = ResearchService([source]).research("topic")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Research source execution failed.")
        self.assertNotIn("private source detail", repr(result))

    def test_malformed_evidence_fails(self):
        source = FakeSource(Result.ok(data=[{"title": "missing fields"}]))
        result = ResearchService([source]).research("topic")
        self.assertFalse(result.success)
        self.assertEqual(
            result.message,
            "Research source returned malformed evidence.",
        )

    def test_non_fact_evidence_is_rejected(self):
        source = FakeSource(
            Result.ok(
                data=[
                    {
                        "source": "catalog",
                        "title": "Claim",
                        "content": "Unverified",
                        "kind": "HYPOTHESIS",
                    }
                ]
            )
        )
        result = ResearchService([source]).research("topic")
        self.assertFalse(result.success)


class ResearchServiceEdgeCaseTests(unittest.TestCase):
    def test_invalid_sources_constructor(self):
        service = ResearchService("not a source list")
        result = service.research("topic")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_none_query_fails(self):
        result = ResearchService().research(None)
        self.assertFalse(result.success)

    def test_non_string_query_fails(self):
        result = ResearchService().research(123)
        self.assertFalse(result.success)

    def test_scope_none_is_valid(self):
        source = FakeSource(
            Result.ok(
                data=[
                    {
                        "source": "s",
                        "title": "t",
                        "content": "c",
                        "kind": "FACT",
                    }
                ]
            )
        )
        result = ResearchService([source]).research("topic", scope=None)
        self.assertTrue(result.success)

    def test_scope_non_string_fails(self):
        result = ResearchService().research("topic", scope=123)
        self.assertFalse(result.success)

    def test_source_without_search_method(self):
        class BadSource:
            pass

        result = ResearchService([BadSource()]).research("topic")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Research source is invalid.")

    def test_source_returns_non_result(self):
        class NonResultSource:
            def search(self, query, scope=None):
                return "not a result"

        result = ResearchService([NonResultSource()]).research("topic")
        self.assertFalse(result.success)
        self.assertIn("invalid Result", result.message)

    def test_source_returns_failure(self):
        source = FakeSource(Result.fail("source error"))
        result = ResearchService([source]).research("topic")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Research source failed.")

    def test_multiple_sources_aggregate(self):
        s1 = FakeSource(
            Result.ok(
                data=[
                    {
                        "source": "a",
                        "title": "A",
                        "content": "Ac",
                        "kind": "FACT",
                    }
                ]
            )
        )
        s2 = FakeSource(
            Result.ok(
                data=[
                    {
                        "source": "b",
                        "title": "B",
                        "content": "Bc",
                        "kind": "FACT",
                    }
                ]
            )
        )
        result = ResearchService([s1, s2]).research("topic")
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.metadata["source_count"], 2)

    def test_normalize_evidence_none_data(self):
        result = ResearchService._normalize_evidence(None)
        self.assertEqual(result, [])

    def test_normalize_evidence_string_data(self):
        result = ResearchService._normalize_evidence("bad")
        self.assertIsNone(result)

    def test_normalize_evidence_bytes_data(self):
        result = ResearchService._normalize_evidence(b"bad")
        self.assertIsNone(result)

    def test_normalize_evidence_mapping_data(self):
        result = ResearchService._normalize_evidence({"key": "val"})
        self.assertIsNone(result)

    def test_normalize_evidence_non_mapping_record(self):
        result = ResearchService._normalize_evidence(["not a dict"])
        self.assertIsNone(result)

    def test_normalize_evidence_missing_required_field(self):
        result = ResearchService._normalize_evidence(
            [{"source": "s", "title": "t", "kind": "FACT"}]
        )
        self.assertIsNone(result)

    def test_normalize_evidence_non_string_field(self):
        result = ResearchService._normalize_evidence(
            [{"source": "s", "title": "t", "content": 123, "kind": "FACT"}]
        )
        self.assertIsNone(result)

    def test_normalize_evidence_non_iterable(self):
        result = ResearchService._normalize_evidence(42)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
