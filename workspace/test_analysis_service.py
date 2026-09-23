import unittest

from core.result import Result
from services.analysis_service import AnalysisService


FACT = {
    "source": "research",
    "content": "Observed fact",
    "kind": "FACT",
}


class FakeAnalyzer:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def analyze(self, evidence, question=None):
        self.calls.append((evidence, question))
        if self.error is not None:
            raise self.error
        return self.result


class AnalysisServiceTests(unittest.TestCase):
    def test_construction_and_deterministic_fact_validation(self):
        result = AnalysisService().analyze([FACT], question="What happened?")
        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["kind"], "FACT")
        self.assertEqual(result.metadata["counts"]["FACT"], 1)

    def test_hypothesis_is_not_promoted_to_fact(self):
        result = AnalysisService().analyze(
            [{"content": "Possible cause", "kind": "hypothesis"}]
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["kind"], "HYPOTHESIS")
        self.assertEqual(result.metadata["counts"]["FACT"], 0)

    def test_analyzer_success_preserves_classifications(self):
        analyzer = FakeAnalyzer(
            Result.ok(
                data=[
                    FACT,
                    {"content": "Possible cause", "kind": "HYPOTHESIS"},
                    {"content": "Suggested next step", "kind": "RECOMMENDATION"},
                ]
            )
        )
        result = AnalysisService(analyzer).analyze([FACT], question="Why?")
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["counts"]["HYPOTHESIS"], 1)
        self.assertEqual(analyzer.calls[0][1], "Why?")

    def test_invalid_evidence_and_question_fail(self):
        service = AnalysisService()
        self.assertFalse(service.analyze("not evidence").success)
        self.assertFalse(service.analyze([FACT], question=" ").success)
        self.assertFalse(
            service.analyze([{"content": "x", "kind": "UNKNOWN"}]).success
        )

    def test_analyzer_failure_and_exception_are_normalized(self):
        failed = FakeAnalyzer(Result.fail("private detail"))
        errored = FakeAnalyzer(error=RuntimeError("private detail"))
        self.assertEqual(
            AnalysisService(failed).analyze([FACT]).message,
            "Analysis provider failed.",
        )
        result = AnalysisService(errored).analyze([FACT])
        self.assertFalse(result.success)
        self.assertNotIn("private detail", repr(result))

    def test_malformed_analyzer_output_fails(self):
        analyzer = FakeAnalyzer(Result.ok(data=[{"kind": "FACT"}]))
        result = AnalysisService(analyzer).analyze([FACT])
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Analysis provider returned malformed data.")


class AnalysisServiceEdgeCaseTests(unittest.TestCase):
    def test_analyzer_without_analyze_method(self):
        class BadAnalyzer:
            pass

        result = AnalysisService(BadAnalyzer()).analyze([FACT])
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Analysis provider is invalid.")

    def test_none_question_is_valid(self):
        result = AnalysisService().analyze([FACT], question=None)
        self.assertTrue(result.success)
        self.assertIsNone(result.metadata["question"])

    def test_empty_evidence_list(self):
        result = AnalysisService().analyze([])
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])
        self.assertEqual(result.metadata["count"], 0)

    def test_multiple_record_types(self):
        records = [
            FACT,
            {"content": "Hypothesis", "kind": "HYPOTHESIS"},
            {"content": "Recommendation", "kind": "RECOMMENDATION"},
            {"content": "Action item", "kind": "ACTION"},
            {"content": "Result achieved", "kind": "RESULT"},
        ]
        result = AnalysisService().analyze(records)
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["counts"]["FACT"], 1)
        self.assertEqual(result.metadata["counts"]["HYPOTHESIS"], 1)

    def test_normalize_records_string_input(self):
        result = AnalysisService._normalize_records("bad")
        self.assertIsNone(result)

    def test_normalize_records_bytes_input(self):
        result = AnalysisService._normalize_records(b"bad")
        self.assertIsNone(result)

    def test_normalize_records_mapping_input(self):
        result = AnalysisService._normalize_records({"key": "val"})
        self.assertIsNone(result)

    def test_normalize_records_non_mapping_item(self):
        result = AnalysisService._normalize_records(["not a dict"])
        self.assertIsNone(result)

    def test_normalize_records_missing_kind(self):
        result = AnalysisService._normalize_records(
            [{"content": "x"}]
        )
        self.assertIsNone(result)

    def test_normalize_records_unknown_kind(self):
        result = AnalysisService._normalize_records(
            [{"content": "x", "kind": "UNKNOWN"}]
        )
        self.assertIsNone(result)

    def test_normalize_records_empty_content(self):
        result = AnalysisService._normalize_records(
            [{"content": "  ", "kind": "FACT"}]
        )
        self.assertIsNone(result)

    def test_analyzer_exception_returns_fail(self):
        analyzer = FakeAnalyzer(error=RuntimeError("crash"))
        result = AnalysisService(analyzer).analyze([FACT])
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Analysis provider execution failed.")

    def test_analyzer_returns_non_result(self):
        class NonResultAnalyzer:
            def analyze(self, evidence, question=None):
                return "not a result"

        result = AnalysisService(NonResultAnalyzer()).analyze([FACT])
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Analysis provider failed.")

    def test_success_metadata_question_stripped(self):
        result = AnalysisService().analyze([FACT], question="  why?  ")
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["question"], "why?")


if __name__ == "__main__":
    unittest.main()
