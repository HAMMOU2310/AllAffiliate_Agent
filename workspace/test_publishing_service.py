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


if __name__ == "__main__":
    unittest.main()
