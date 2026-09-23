import os
import tempfile
import unittest
from unittest.mock import MagicMock

from agents.memory_agent import MemoryAgent
from core.result import Result
from core.task import Task
from memory.memory_manager import MemoryManager


class MemoryAgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "mem.db")

    def tearDown(self):
        import shutil
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def _agent(self):
        return MemoryAgent(
            memory_manager=MemoryManager(self.db_path)
        )

    def test_none_memory_manager_fails(self):
        agent = MemoryAgent(memory_manager=None)
        task = Task(
            task_type="memory",
            command="save",
            data={"operation": "save", "memory_type": "session", "key": "k", "value": "v"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_no_operation_fails(self):
        agent = self._agent()
        task = Task(task_type="memory", command="", data={})
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_unsupported_operation_fails(self):
        agent = self._agent()
        task = Task(task_type="memory", command="fly", data={"operation": "fly_to_moon"})
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_save_operation(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "k1", "value": "v1"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_get_operation(self):
        agent = self._agent()
        agent.execute(Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "gk", "value": "gv"},
        ))
        task = Task(
            task_type="memory", command="get",
            data={"operation": "get", "memory_type": "session", "key": "gk"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_get_entry_operation(self):
        agent = self._agent()
        agent.execute(Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "ek", "value": "ev"},
        ))
        task = Task(
            task_type="memory", command="get_entry",
            data={"operation": "get_entry", "memory_type": "session", "key": "ek"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_search_operation(self):
        agent = self._agent()
        agent.execute(Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "search_alpha", "value": "x"},
        ))
        task = Task(
            task_type="memory", command="search",
            data={"operation": "search", "query": "search"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_list_operation(self):
        agent = self._agent()
        agent.execute(Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "lk", "value": "lv"},
        ))
        task = Task(
            task_type="memory", command="list",
            data={"operation": "list"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_delete_operation_not_found(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="delete",
            data={"operation": "delete", "memory_type": "session", "key": "nonexistent"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_delete_operation_found(self):
        agent = self._agent()
        agent.execute(Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "dk", "value": "dv"},
        ))
        task = Task(
            task_type="memory", command="delete",
            data={"operation": "delete", "memory_type": "session", "key": "dk"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_clear_session_operation(self):
        agent = self._agent()
        agent.execute(Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "cs", "value": "cv", "session_id": "test-session"},
        ))
        task = Task(
            task_type="memory", command="clear_session",
            data={"operation": "clear_session", "session_id": "test-session"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_clear_session_empty_id_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="clear_session",
            data={"operation": "clear_session", "session_id": ""},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_count_operation(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="count",
            data={"operation": "count"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_health_check_ok(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="health_check",
            data={"operation": "health_check"},
        )
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_health_check_fail(self):
        agent = self._agent()
        agent.memory_manager.database_path = "/nonexistent_root/db/memory.db"
        task = Task(
            task_type="memory", command="health_check",
            data={"operation": "health_check"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_save_missing_memory_type_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="save",
            data={"operation": "save", "key": "k", "value": "v"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_save_missing_key_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "value": "v"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_get_missing_key_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="get",
            data={"operation": "get", "memory_type": "session"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_delete_missing_key_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="delete",
            data={"operation": "delete", "memory_type": "session"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)


class MemoryAgentExceptionPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "mem.db")

    def tearDown(self):
        import shutil
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def _agent(self):
        return MemoryAgent(
            memory_manager=MemoryManager(self.db_path)
        )

    def test_manager_exception_returns_fail(self):
        agent = self._agent()
        agent.memory_manager.save = MagicMock(side_effect=RuntimeError("db crash"))
        task = Task(
            task_type="memory", command="save",
            data={"operation": "save", "memory_type": "session", "key": "k", "value": "v"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)
        self.assertIn("db crash", result.message)


class MemoryAgentMissingFieldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "mem.db")

    def tearDown(self):
        import shutil
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp, ignore_errors=True)

    def _agent(self):
        return MemoryAgent(memory_manager=MemoryManager(self.db_path))

    def test_get_missing_memory_type_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="get",
            data={"operation": "get", "key": "k"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_get_entry_missing_memory_type_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="get_entry",
            data={"operation": "get_entry", "key": "k"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_delete_missing_memory_type_fails(self):
        agent = self._agent()
        task = Task(
            task_type="memory", command="delete",
            data={"operation": "delete", "key": "k"},
        )
        result = agent.execute(task)
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()
