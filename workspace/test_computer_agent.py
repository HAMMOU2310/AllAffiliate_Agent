import unittest
from types import SimpleNamespace

from agents.computer_agent import ComputerAgent
from core.result import Result
from services.computer_service import ComputerService


class FakeComputerAdapter:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or Result.ok(data={"verified": True})

    def execute(self, operation, payload=None):
        self.calls.append((operation, payload))
        return self.result


class ComputerAgentTests(unittest.TestCase):
    def test_permitted_service_delegates_to_replaceable_adapter(self):
        adapter = FakeComputerAdapter()
        result = ComputerService(adapter, permitted=True).execute("screen", {"region": "main"})
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls, [("screen", {"region": "main"})])

    def test_permission_is_required_and_blocks_adapter_execution(self):
        adapter = FakeComputerAdapter()
        result = ComputerService(adapter).execute("keyboard", {"key": "A"})
        self.assertFalse(result.success)
        self.assertIn("permission", result.message.lower())
        self.assertEqual(adapter.calls, [])

    def test_invalid_operation_and_missing_adapter_fail(self):
        self.assertFalse(ComputerService(FakeComputerAdapter(), permitted=True).execute("delete").success)
        self.assertFalse(ComputerService(permitted=True).execute("screen").success)

    def test_agent_delegates_safe_verification_operation(self):
        adapter = FakeComputerAdapter()
        service = ComputerService(adapter, permitted=True)
        agent = ComputerAgent({"computer_service": service})
        result = agent.execute(SimpleNamespace(command="screen state"))
        self.assertTrue(result.success)
        self.assertEqual(adapter.calls, [("verify_state", "screen state")])


if __name__ == "__main__":
    unittest.main()
