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


if __name__ == "__main__":
    unittest.main()
