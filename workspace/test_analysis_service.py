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


if __name__ == "__main__":
    unittest.main()
