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


class FakeFailingAdapter:
    def execute(self, operation, payload=None):
        return Result.fail("adapter failed")


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

    def test_search_command_routes_to_extract(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command="search python affiliate"))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "extract")
        self.assertEqual(adapter.calls[0][1], "python affiliate")

    def test_search_command_with_arabic_prefix(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command="\u0627\u0628\u062d\u062b python"))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "extract")
        self.assertEqual(adapter.calls[0][1], "python")

    def test_inspect_command_routes_to_inspect(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command="inspect page content"))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "inspect")
        self.assertEqual(adapter.calls[0][1], "page content")

    def test_unknown_command_routes_to_execute_workflow(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command="some other command"))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "execute_workflow")

    def test_missing_service_fails(self):
        agent = BrowserAgent({"browser_service": None})
        result = agent.execute(SimpleNamespace(command="search query"))
        self.assertFalse(result.success)
        self.assertIn("not registered", result.message.lower())

    def test_non_string_command_fails(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command=123))
        self.assertFalse(result.success)

    def test_adapter_failure_propagates(self):
        agent = BrowserAgent({"browser_service": BrowserService(FakeFailingAdapter())})
        result = agent.execute(SimpleNamespace(command="search query"))
        self.assertFalse(result.success)
        self.assertEqual(result.message, "adapter failed")

    def test_empty_search_query_falls_to_workflow(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command="search "))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "execute_workflow")

    def test_search_without_query_falls_to_workflow(self):
        adapter = FakeAdapter()
        agent = BrowserAgent({"browser_service": BrowserService(adapter)})
        result = agent.execute(SimpleNamespace(command="search"))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls[0][0], "execute_workflow")


if __name__ == "__main__": unittest.main()
