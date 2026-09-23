import unittest

from core.result import Result
from services.publishing_service import PublishingService


class FakeAdapter:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def publish(self, asset, destination):
        self.calls.append((asset, destination))
        if self.error is not None:
            raise self.error
        return self.result


class PublishingServiceTests(unittest.TestCase):
    def test_success_routes_to_adapter(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        result = PublishingService(adapter).publish({"title": "asset"}, "platform")
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["destination"], "platform")

    def test_blocked_fails_closed(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        result = PublishingService(adapter).publish(
            {"title": "asset", "policy": {"decision": "BLOCKED"}}, "platform"
        )
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Publishing blocked by policy.")
        self.assertEqual(adapter.calls, [])

    def test_invalid_missing_and_adapter_failures(self):
        self.assertFalse(PublishingService().publish({}, "platform").success)
        self.assertFalse(PublishingService().publish({"title": "a"}, "").success)
        failed = PublishingService(FakeAdapter(Result.fail("private"))).publish(
            {"title": "a"}, "platform"
        )
        errored = PublishingService(FakeAdapter(error=RuntimeError("private"))).publish(
            {"title": "a"}, "platform"
        )
        self.assertEqual(failed.message, "Publishing adapter failed.")
        self.assertEqual(errored.message, "Publishing adapter execution failed.")


class PublishingServiceEdgeCaseTests(unittest.TestCase):
    def test_non_callable_adapter_fails(self):
        result = PublishingService("not_callable").publish({"title": "a"}, "platform")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Publishing adapter is invalid.")

    def test_adapter_returns_non_result_fails(self):
        result = PublishingService(FakeAdapter(result="not_a_result")).publish({"title": "a"}, "platform")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Publishing adapter failed.")

    def test_no_adapter_fails(self):
        result = PublishingService().publish({"title": "a"}, "platform")
        self.assertFalse(result.success)
        self.assertIn("adapter", result.message.lower())

    def test_non_dict_asset_fails(self):
        result = PublishingService(FakeAdapter(Result.ok())).publish("string", "platform")
        self.assertFalse(result.success)

    def test_empty_string_destination_fails(self):
        result = PublishingService(FakeAdapter(Result.ok())).publish({"title": "a"}, "")
        self.assertFalse(result.success)

    def test_whitespace_destination_fails(self):
        result = PublishingService(FakeAdapter(Result.ok())).publish({"title": "a"}, "   ")
        self.assertFalse(result.success)

    def test_non_string_destination_fails(self):
        result = PublishingService(FakeAdapter(Result.ok())).publish({"title": "a"}, 123)
        self.assertFalse(result.success)

    def test_policy_non_blocked_passes_through(self):
        for decision in ("ALLOWED", "REVIEW_REQUIRED"):
            adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
            asset = {"title": "a", "policy": {"decision": decision}}
            result = PublishingService(adapter).publish(asset, "platform")
            self.assertTrue(result.success, f"Failed for decision: {decision}")
            self.assertEqual(len(adapter.calls), 1)

    def test_policy_blocked_does_not_call_adapter(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        asset = {"title": "a", "policy": {"decision": "BLOCKED"}}
        PublishingService(adapter).publish(asset, "platform")
        self.assertEqual(adapter.calls, [])

    def test_asset_without_policy_key_passes_through(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        result = PublishingService(adapter).publish({"title": "a"}, "platform")
        self.assertTrue(result.success)
        self.assertEqual(len(adapter.calls), 1)

    def test_asset_with_non_dict_policy_passes_through(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        result = PublishingService(adapter).publish({"title": "a", "policy": "not_dict"}, "platform")
        self.assertTrue(result.success)

    def test_asset_with_policy_missing_decision_passes_through(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        result = PublishingService(adapter).publish({"title": "a", "policy": {"reasons": ["r"]}}, "platform")
        self.assertTrue(result.success)

    def test_destination_stripped(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        result = PublishingService(adapter).publish({"title": "a"}, "  platform  ")
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["destination"], "platform")

    def test_adapter_receives_copy_of_asset(self):
        captured = []
        class CapturingAdapter:
            def publish(self, asset, destination):
                captured.append(dict(asset))
                return Result.ok(data={"id": "1"})
        asset = {"title": "original"}
        PublishingService(CapturingAdapter()).publish(asset, "platform")
        self.assertEqual(captured[0]["title"], "original")

    def test_adapter_receives_stripped_destination(self):
        captured = []
        class CapturingAdapter:
            def publish(self, asset, destination):
                captured.append(destination)
                return Result.ok(data={"id": "1"})
        PublishingService(CapturingAdapter()).publish({"title": "a"}, "  platform  ")
        self.assertEqual(captured[0], "platform")

    def test_metadata_contains_destination(self):
        adapter = FakeAdapter(Result.ok(data={"remote_id": "1"}))
        result = PublishingService(adapter).publish({"title": "a"}, "platform")
        self.assertEqual(result.metadata["destination"], "platform")


if __name__ == "__main__":
    unittest.main()
