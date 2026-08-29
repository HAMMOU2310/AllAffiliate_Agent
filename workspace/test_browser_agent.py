import unittest
from types import SimpleNamespace
from core.result import Result
from services.browser_service import BrowserService
from agents.browser_agent import BrowserAgent


class FakeAdapter:
    def __init__(self): self.calls = []
    def execute(self, operation, payload=None):
        self.calls.append((operation, payload))
        return Result.ok(data={"ok": True})


class BrowserAgentTests(unittest.TestCase):
    def test_service_operations_delegate_to_adapter(self):
        adapter = FakeAdapter()
        result = BrowserService(adapter).execute("navigate", "https://example.test")
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "navigate")

    def test_agent_delegates_workflow(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command="workflow"))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "execute_workflow")

    def test_invalid_and_missing_adapter_fail(self):
        self.assertFalse(BrowserService().execute("navigate").success)
        self.assertFalse(BrowserService(FakeAdapter()).execute("delete").success)


if __name__ == "__main__": unittest.main()
