import unittest

from core.result import Result
from services.policy_service import PolicyService


class FakeEvaluator:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def evaluate(self, asset):
        if self.error is not None:
            raise self.error
        return self.result


class PolicyServiceTests(unittest.TestCase):
    def test_construction_and_missing_evaluator(self):
        self.assertIsInstance(PolicyService(), PolicyService)
        result = PolicyService().evaluate({"title": "asset"})
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No policy evaluator is registered.")

    def test_all_decisions_are_representable(self):
        for decision, publishable in (
            ("ALLOWED", True),
            ("BLOCKED", False),
            ("REVIEW_REQUIRED", False),
        ):
            evaluator = FakeEvaluator(
                Result.ok(data={"decision": decision, "reasons": ["reason"]})
            )
            result = PolicyService(evaluator).evaluate({"title": "asset"})
            self.assertTrue(result.success)
            self.assertEqual(result.data["decision"], decision)
            self.assertEqual(result.data["publishable"], publishable)

    def test_invalid_asset_and_output_fail(self):
        evaluator = FakeEvaluator(
            Result.ok(data={"decision": "UNKNOWN", "reasons": ["reason"]})
        )
        service = PolicyService(evaluator)
        self.assertFalse(service.evaluate({}).success)
        self.assertFalse(service.evaluate({"title": "asset"}).success)

        malformed = FakeEvaluator(Result.ok(data={"decision": "ALLOWED"}))
        self.assertFalse(PolicyService(malformed).evaluate({"title": "asset"}).success)

    def test_failure_and_exception_are_normalized(self):
        failed = PolicyService(FakeEvaluator(Result.fail("private detail"))).evaluate(
            {"title": "asset"}
        )
        errored = PolicyService(
            FakeEvaluator(error=RuntimeError("private detail"))
        ).evaluate({"title": "asset"})
        self.assertEqual(failed.message, "Policy evaluator failed.")
        self.assertEqual(errored.message, "Policy evaluator execution failed.")
        self.assertNotIn("private detail", repr(errored))


class PolicyServiceEdgeCaseTests(unittest.TestCase):
    def test_non_callable_evaluator_fails(self):
        result = PolicyService("not_callable").evaluate({"title": "asset"})
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Policy evaluator is invalid.")

    def test_evaluator_returns_non_result_fails(self):
        result = PolicyService(FakeEvaluator(result="not_a_result")).evaluate({"title": "asset"})
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Policy evaluator failed.")

    def test_evaluator_returns_non_dict_data_fails(self):
        result = PolicyService(FakeEvaluator(Result.ok(data="string_data"))).evaluate({"title": "asset"})
        self.assertFalse(result.success)
        self.assertIn("malformed", result.message.lower())

    def test_empty_asset_fails(self):
        result = PolicyService(FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": ["r"]}))).evaluate({})
        self.assertFalse(result.success)

    def test_non_dict_asset_fails(self):
        result = PolicyService(FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": ["r"]}))).evaluate("string")
        self.assertFalse(result.success)

    def test_case_insensitive_decision(self):
        for decision in ("allowed", "Allowed", "ALLOWED"):
            evaluator = FakeEvaluator(Result.ok(data={"decision": decision, "reasons": ["r"]}))
            result = PolicyService(evaluator).evaluate({"title": "a"})
            self.assertTrue(result.success, f"Failed for decision: {decision}")
            self.assertEqual(result.data["decision"], decision.upper())

    def test_empty_reasons_list_is_valid(self):
        evaluator = FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": []}))
        result = PolicyService(evaluator).evaluate({"title": "a"})
        self.assertTrue(result.success)
        self.assertEqual(result.data["reasons"], [])

    def test_non_list_reasons_fails(self):
        evaluator = FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": "string"}))
        result = PolicyService(evaluator).evaluate({"title": "a"})
        self.assertFalse(result.success)

    def test_reasons_with_non_string_items_fails(self):
        evaluator = FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": [123]}))
        result = PolicyService(evaluator).evaluate({"title": "a"})
        self.assertFalse(result.success)

    def test_reasons_with_empty_string_fails(self):
        evaluator = FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": ["  "]}))
        result = PolicyService(evaluator).evaluate({"title": "a"})
        self.assertFalse(result.success)

    def test_reasons_stripped_in_output(self):
        evaluator = FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": ["  reason  "]}))
        result = PolicyService(evaluator).evaluate({"title": "a"})
        self.assertTrue(result.success)
        self.assertEqual(result.data["reasons"], ["reason"])

    def test_publishable_true_only_for_allowed(self):
        for decision, expected in (("ALLOWED", True), ("BLOCKED", False), ("REVIEW_REQUIRED", False)):
            evaluator = FakeEvaluator(Result.ok(data={"decision": decision, "reasons": ["r"]}))
            result = PolicyService(evaluator).evaluate({"title": "a"})
            self.assertEqual(result.data["publishable"], expected)

    def test_metadata_contains_decision(self):
        evaluator = FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": ["r"]}))
        result = PolicyService(evaluator).evaluate({"title": "a"})
        self.assertEqual(result.metadata["decision"], "ALLOWED")

    def test_asset_passed_to_evaluator(self):
        captured = []
        class CapturingEvaluator:
            def evaluate(self, asset):
                captured.append(dict(asset))
                return Result.ok(data={"decision": "ALLOWED", "reasons": ["r"]})
        asset = {"title": "test"}
        PolicyService(CapturingEvaluator()).evaluate(asset)
        self.assertEqual(captured[0]["title"], "test")

    def test_asset_is_copied_not_mutated(self):
        asset = {"title": "original"}
        PolicyService(FakeEvaluator(Result.ok(data={"decision": "ALLOWED", "reasons": ["r"]}))).evaluate(asset)
        self.assertEqual(asset["title"], "original")

    def test_unknown_decision_fails(self):
        evaluator = FakeEvaluator(Result.ok(data={"decision": "UNKNOWN", "reasons": ["r"]}))
        result = PolicyService(evaluator).evaluate({"title": "a"})
        self.assertFalse(result.success)
        self.assertIn("decision", result.message.lower())


if __name__ == "__main__":
    unittest.main()
