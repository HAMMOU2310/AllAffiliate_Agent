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


if __name__ == "__main__":
    unittest.main()
