import unittest

from core.result import Result
from services.diagnosis_service import DiagnosisService


class FakeAnalyzer:
    def __init__(self, result=None, error=None):
        self.result, self.error = result, error

    def analyze(self, asset_id, observations):
        if self.error:
            raise self.error
        return self.result


class DiagnosisServiceTests(unittest.TestCase):
    def test_fact_only_diagnosis_does_not_invent_cause(self):
        result = DiagnosisService().diagnose("asset", [{"content": "views fell"}])
        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["kind"], "FACT")

    def test_analyzer_preserves_classifications(self):
        result = DiagnosisService(FakeAnalyzer(Result.ok(data=[
            {"content": "possible cause", "kind": "HYPOTHESIS"},
            {"content": "inspect funnel", "kind": "RECOMMENDATION"},
        ]))).diagnose("asset", [{"content": "views fell"}])
        self.assertEqual([x["kind"] for x in result.data], ["HYPOTHESIS", "RECOMMENDATION"])

    def test_invalid_and_failure_paths(self):
        self.assertFalse(DiagnosisService().diagnose("", []).success)
        self.assertFalse(DiagnosisService().diagnose("a", [{"x": 1}]).success)
        failed = DiagnosisService(FakeAnalyzer(Result.fail("private"))).diagnose("a", [])
        errored = DiagnosisService(FakeAnalyzer(error=RuntimeError("private"))).diagnose("a", [])
        self.assertEqual(failed.message, "Diagnosis analyzer failed.")
        self.assertEqual(errored.message, "Diagnosis analyzer execution failed.")


if __name__ == "__main__":
    unittest.main()
