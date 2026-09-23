import unittest
from unittest.mock import MagicMock, patch

from agents.master_agent import MasterAgent
from core.result import Result
from core.task import Task


def _make_master():
    """Build a MasterAgent with all heavy deps mocked."""
    with patch("agents.master_agent.ServiceContainer") as mock_sc, \
         patch("agents.master_agent.CommandParser") as mock_cp, \
         patch("agents.master_agent.TaskRouter") as mock_tr, \
         patch("agents.master_agent.MemoryAgent") as mock_ma, \
         patch("agents.master_agent.Console") as mock_console:

        mock_memory = MagicMock()
        mock_memory.execute.return_value = Result.ok(
            data=None,
            message="ok",
        )
        mock_ma.return_value = mock_memory

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_memory
        mock_tr.return_value.registry = mock_registry
        mock_tr.return_value.route.return_value = Result.ok(data="routed", message="done")

        mock_parser = MagicMock()
        mock_parser.parse.return_value = Task(
            task_type="coding",
            command="list",
            data={},
        )
        mock_cp.return_value = mock_parser

        agent = MasterAgent()

    return agent, mock_memory, mock_registry, mock_parser, mock_console


class MasterAgentSessionTests(unittest.TestCase):
    def test_start_session_returns_uuid(self):
        agent, *_ = _make_master()
        sid = agent.start_session()
        self.assertIsInstance(sid, str)
        self.assertEqual(len(sid), 36)

    def test_start_session_updates_session_id(self):
        agent, *_ = _make_master()
        old = agent.session_id
        new = agent.start_session()
        self.assertNotEqual(old, new)
        self.assertEqual(agent.session_id, new)

    def test_end_session_with_no_session_id_fails(self):
        agent, *_ = _make_master()
        agent.session_id = ""
        result = agent.end_session()
        self.assertFalse(result.success)

    def test_end_session_with_active_session(self):
        agent, mock_memory, *_ = _make_master()
        agent.session_id = "test-session-123"
        mock_memory.execute.return_value = Result.ok(data={"deleted_count": 0})
        result = agent.end_session()
        self.assertTrue(result.success)
        self.assertEqual(agent.session_id, "")

    def test_end_session_clears_session_id_on_success(self):
        agent, mock_memory, *_ = _make_master()
        agent.session_id = "active"
        mock_memory.execute.return_value = Result.ok(data={"deleted_count": 2})
        agent.end_session()
        self.assertEqual(agent.session_id, "")

    def test_end_session_preserves_session_id_on_failure(self):
        agent, mock_memory, *_ = _make_master()
        agent.session_id = "active"
        mock_memory.execute.return_value = Result.fail(message="db error")
        agent.end_session()
        self.assertEqual(agent.session_id, "active")

    def test_end_session_no_memory_agent_fails(self):
        agent, *_ = _make_master()
        agent.memory_agent = None
        agent.session_id = "x"
        result = agent.end_session()
        self.assertFalse(result.success)


class MasterAgentExecuteTests(unittest.TestCase):
    def test_execute_routes_command(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        task = Task(task_type="coding", command="list", data={})
        mock_parser.parse.return_value = task
        result = agent.execute("list")
        self.assertTrue(result.success)

    def test_execute_stores_last_command_in_context(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        task = Task(task_type="coding", command="list", data={})
        mock_parser.parse.return_value = task
        agent.execute("list")
        calls = mock_memory.execute.call_args_list
        save_calls = [c for c in calls if c[0][0].data.get("operation") == "save"]
        self.assertGreater(len(save_calls), 0)

    def test_execute_stores_last_result_in_context(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        task = Task(task_type="coding", command="list", data={})
        mock_parser.parse.return_value = task
        agent.execute("list")
        calls = mock_memory.execute.call_args_list
        save_calls = [c for c in calls if c[0][0].data.get("key") == "last_result"]
        self.assertGreater(len(save_calls), 0)

    def test_execute_empty_session_starts_new(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        agent.session_id = ""
        task = Task(task_type="coding", command="list", data={})
        mock_parser.parse.return_value = task
        agent.execute("list")
        self.assertNotEqual(agent.session_id, "")

    def test_execute_exception_returns_fail(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        mock_parser.parse.side_effect = RuntimeError("boom")
        result = agent.execute("bad")
        self.assertFalse(result.success)
        self.assertIn("boom", result.message)


class MasterAgentContextTests(unittest.TestCase):
    def test_get_context_no_memory_agent(self):
        agent, *_ = _make_master()
        agent.memory_agent = None
        result = agent.get_context("key")
        self.assertFalse(result.success)

    def test_get_context_no_session_id(self):
        agent, *_ = _make_master()
        agent.session_id = ""
        result = agent.get_context("key")
        self.assertFalse(result.success)

    def test_get_context_delegates_to_memory(self):
        agent, mock_memory, *_ = _make_master()
        agent.session_id = "s1"
        mock_memory.execute.return_value = Result.ok(data={"val": 1})
        result = agent.get_context("last_command")
        self.assertTrue(result.success)

    def test_get_execution_context_no_memory(self):
        agent, *_ = _make_master()
        agent.memory_agent = None
        ctx = agent._get_execution_context()
        self.assertEqual(ctx, {})

    def test_get_execution_context_no_session(self):
        agent, *_ = _make_master()
        agent.session_id = ""
        ctx = agent._get_execution_context()
        self.assertEqual(ctx, {})

    def test_get_execution_context_with_data(self):
        agent, mock_memory, *_ = _make_master()
        agent.session_id = "s1"
        call_count = [0]
        def side_effect(task):
            call_count[0] += 1
            if call_count[0] == 1:
                return Result.ok(data={"command": "list"})
            return Result.ok(data={"success": True})
        mock_memory.execute.side_effect = side_effect
        ctx = agent._get_execution_context()
        self.assertIn("last_command", ctx)
        self.assertIn("last_result", ctx)


class MasterAgentSaveContextTests(unittest.TestCase):
    def test_save_context_no_memory_agent(self):
        agent, *_ = _make_master()
        agent.memory_agent = None
        agent._save_context("k", "v")

    def test_save_context_no_session(self):
        agent, *_ = _make_master()
        agent.session_id = ""
        agent._save_context("k", "v")


class MasterAgentDisplayTests(unittest.TestCase):
    def test_display_result_calls_console(self):
        agent, _, _, _, mock_console_cls = _make_master()
        mock_console = mock_console_cls.return_value
        result = Result.ok(data="some data", message="hello")
        agent.display_result(result)
        self.assertTrue(mock_console.print.called)

    def test_display_result_with_errors(self):
        agent, _, _, _, mock_console_cls = _make_master()
        mock_console = mock_console_cls.return_value
        result = Result.fail(message="err", errors=["e1", "e2"])
        agent.display_result(result)
        calls = [str(c) for c in mock_console.print.call_args_list]
        self.assertTrue(any("e1" in c for c in calls))


class MasterAgentDisplayVariationTests(unittest.TestCase):
    def test_display_message_only(self):
        agent, _, _, _, mock_console_cls = _make_master()
        mock_console = mock_console_cls.return_value
        result = Result.ok(message="msg only")
        agent.display_result(result)
        self.assertTrue(mock_console.print.called)

    def test_display_data_only(self):
        agent, _, _, _, mock_console_cls = _make_master()
        mock_console = mock_console_cls.return_value
        result = Result.ok(data={"key": "val"})
        agent.display_result(result)
        self.assertTrue(mock_console.print.called)

    def test_display_empty_result(self):
        agent, _, _, _, mock_console_cls = _make_master()
        mock_console = mock_console_cls.return_value
        result = Result.ok()
        agent.display_result(result)
        self.assertFalse(mock_console.print.called)


class MasterAgentExecuteContextTests(unittest.TestCase):
    def test_execute_propagates_context_to_task(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        agent.session_id = "ctx-session"

        call_idx = [0]
        def memory_side_effect(task):
            call_idx[0] += 1
            op = task.data.get("operation")
            if op == "get" and task.data.get("key") == "last_command":
                return Result.ok(data={"command": "prev"})
            if op == "get" and task.data.get("key") == "last_result":
                return Result.ok(data={"success": True})
            return Result.ok(data=None)
        mock_memory.execute.side_effect = memory_side_effect

        task = Task(task_type="coding", command="list", data={})
        mock_parser.parse.return_value = task
        agent.execute("list")

        self.assertIn("context", task.data)

    def test_execute_without_context_has_no_context_key(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        agent.session_id = "no-ctx"

        def memory_side_effect(task):
            return Result.ok(data=None)
        mock_memory.execute.side_effect = memory_side_effect

        task = Task(task_type="coding", command="list", data={})
        mock_parser.parse.return_value = task
        agent.execute("list")

        self.assertNotIn("context", task.data)

    def test_execute_router_exception_returns_fail(self):
        agent, mock_memory, _, mock_parser, _ = _make_master()
        task = Task(task_type="coding", command="list", data={})
        mock_parser.parse.return_value = task
        mock_memory.execute.return_value = Result.ok(data=None)

        from unittest.mock import PropertyMock
        agent.router = MagicMock()
        agent.router.route.side_effect = RuntimeError("route boom")
        result = agent.execute("list")
        self.assertFalse(result.success)
        self.assertIn("route boom", result.message)


class MasterAgentEndSessionTaskTests(unittest.TestCase):
    def test_end_session_passes_correct_task(self):
        agent, mock_memory, *_ = _make_master()
        agent.session_id = "verify-session"
        mock_memory.execute.return_value = Result.ok(data={"deleted_count": 0})
        agent.end_session()

        call = mock_memory.execute.call_args
        task = call[0][0]
        self.assertEqual(task.data["operation"], "clear_session")
        self.assertEqual(task.data["session_id"], "verify-session")


if __name__ == "__main__":
    unittest.main()
