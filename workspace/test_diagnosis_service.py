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


class DiagnosisServiceEdgeCaseTests(unittest.TestCase):
    def test_non_callable_analyzer_fails(self):
        result = DiagnosisService("not_callable").diagnose("asset", [])
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Diagnosis analyzer is invalid.")

    def test_analyzer_returns_non_result_fails(self):
        result = DiagnosisService(FakeAnalyzer(result="not_a_result")).diagnose("asset", [])
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Diagnosis analyzer failed.")

    def test_whitespace_asset_id_fails(self):
        result = DiagnosisService().diagnose("   ", [])
        self.assertFalse(result.success)

    def test_normalize_bytes_input_fails(self):
        result = DiagnosisService().diagnose("asset", b"bad")
        self.assertFalse(result.success)
        self.assertIn("malformed", result.message.lower())

    def test_normalize_string_input_fails(self):
        result = DiagnosisService().diagnose("asset", "bad")
        self.assertFalse(result.success)

    def test_normalize_mapping_input_fails(self):
        result = DiagnosisService().diagnose("asset", {"bad": "dict"})
        self.assertFalse(result.success)

    def test_normalize_non_mapping_record_fails(self):
        result = DiagnosisService().diagnose("asset", ["string_record"])
        self.assertFalse(result.success)

    def test_normalize_missing_content_field_fails(self):
        result = DiagnosisService().diagnose("asset", [{"kind": "FACT"}])
        self.assertFalse(result.success)

    def test_normalize_content_not_string_fails(self):
        result = DiagnosisService().diagnose("asset", [{"content": 123}])
        self.assertFalse(result.success)

    def test_normalize_empty_content_fails(self):
        result = DiagnosisService().diagnose("asset", [{"content": "   "}])
        self.assertFalse(result.success)

    def test_normalize_non_string_kind_fails(self):
        result = DiagnosisService().diagnose("asset", [{"content": "x", "kind": 123}])
        self.assertFalse(result.success)

    def test_normalize_unknown_kind_fails(self):
        result = DiagnosisService().diagnose("asset", [{"content": "x", "kind": "UNKNOWN"}])
        self.assertFalse(result.success)

    def test_default_kind_is_fact_when_no_analyzer(self):
        result = DiagnosisService().diagnose("asset", [{"content": "observed"}])
        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["kind"], "FACT")
        self.assertEqual(result.data[0]["content"], "observed")

    def test_metadata_contains_asset_id_and_count(self):
        result = DiagnosisService().diagnose("my-asset", [{"content": "a"}, {"content": "b"}])
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["asset_id"], "my-asset")
        self.assertEqual(result.metadata["count"], 2)

    def test_analyzer_output_normalized_after_success(self):
        analyzer_result = Result.ok(data=[
            {"content": "  hypothesis  ", "kind": "HYPOTHESIS"},
            {"content": "recommendation", "kind": "RECOMMENDATION"},
        ])
        result = DiagnosisService(FakeAnalyzer(analyzer_result)).diagnose("asset", [])
        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["content"], "hypothesis")
        self.assertEqual(result.data[1]["kind"], "RECOMMENDATION")

    def test_analyzer_returning_none_kind_uses_default_false(self):
        analyzer_result = Result.ok(data=[{"content": "info"}])
        result = DiagnosisService(FakeAnalyzer(analyzer_result)).diagnose("asset", [])
        self.assertFalse(result.success)
        self.assertIn("malformed", result.message.lower())

    def test_analyzer_returning_empty_list_succeeds(self):
        result = DiagnosisService(FakeAnalyzer(Result.ok(data=[]))).diagnose("asset", [])
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])

    def test_analyzer_returning_fails_result_fails(self):
        result = DiagnosisService(FakeAnalyzer(Result.fail("bad"))).diagnose("asset", [{"content": "x"}])
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Diagnosis analyzer failed.")

    def test_asset_id_stripped_in_metadata(self):
        result = DiagnosisService().diagnose("  padded  ", [{"content": "x"}])
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["asset_id"], "padded")

    def test_analyzer_receives_stripped_asset_id(self):
        captured = []
        class CapturingAnalyzer:
            def analyze(self, asset_id, observations):
                captured.append(asset_id)
                return Result.ok(data=[{"content": "ok", "kind": "FACT"}])
        DiagnosisService(CapturingAnalyzer()).diagnose("  padded  ", [])
        self.assertEqual(captured[0], "padded")


if __name__ == "__main__":
    unittest.main()
