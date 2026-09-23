import os
import unittest

from core.command_dispatcher import CommandDispatcher
from core.result import Result


class FakeProjectManager:
    def __init__(self):
        self.projects = []

    def create_project(self, name):
        self.projects.append(name)
        return Result.ok(data=name, message=f"Created: {name}")

    def list_projects(self):
        return Result.ok(data=self.projects)


class FakeServices:
    def __init__(self):
        self._data = {"project_manager": FakeProjectManager()}

    def get(self, key):
        return self._data.get(key)


class CommandDispatcherDispatchTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = CommandDispatcher(FakeServices())

    def test_non_string_command_fails(self):
        result = self.dispatcher.dispatch(123)
        self.assertFalse(result.success)

    def test_empty_string_fails(self):
        result = self.dispatcher.dispatch("")
        self.assertFalse(result.success)

    def test_whitespace_only_fails(self):
        result = self.dispatcher.dispatch("   ")
        self.assertFalse(result.success)

    def test_unsupported_command_fails(self):
        result = self.dispatcher.dispatch("unknown command")
        self.assertFalse(result.success)

    def test_create_file_dispatches(self):
        result = self.dispatcher.dispatch("create file workspace/_test_dispatch__.txt")
        self.assertIsInstance(result, Result)
        import os
        if os.path.exists("workspace/_test_dispatch__.txt"):
            os.remove("workspace/_test_dispatch__.txt")

    def test_create_empty_filename_fails(self):
        result = self.dispatcher.dispatch("create file ")
        self.assertFalse(result.success)

    def test_run_empty_filename_fails(self):
        result = self.dispatcher.dispatch("run ")
        self.assertFalse(result.success)

    def test_read_empty_filename_fails(self):
        result = self.dispatcher.dispatch("read ")
        self.assertFalse(result.success)

    def test_delete_empty_filename_fails(self):
        result = self.dispatcher.dispatch("delete ")
        self.assertFalse(result.success)

    def test_write_without_pipe_fails(self):
        result = self.dispatcher.dispatch("write file.txt")
        self.assertFalse(result.success)

    def test_append_without_pipe_fails(self):
        result = self.dispatcher.dispatch("append file.txt")
        self.assertFalse(result.success)

    def test_list_dispatches(self):
        result = self.dispatcher.dispatch("list")
        self.assertIsInstance(result, Result)

    def test_create_project_dispatches(self):
        result = self.dispatcher.dispatch("create project test_proj")
        self.assertTrue(result.success)

    def test_list_projects_dispatches(self):
        result = self.dispatcher.dispatch("list projects")
        self.assertTrue(result.success)

    def test_arabic_create_dispatches(self):
        result = self.dispatcher.dispatch("أنشئ ملف workspace/_test_ar__.txt")
        self.assertIsInstance(result, Result)
        import os
        if os.path.exists("workspace/_test_ar__.txt"):
            os.remove("workspace/_test_ar__.txt")

    def test_arabic_run_empty_fails(self):
        result = self.dispatcher.dispatch("شغل ")
        self.assertFalse(result.success)

    def test_arabic_read_empty_fails(self):
        result = self.dispatcher.dispatch("اقرأ ")
        self.assertFalse(result.success)

    def test_arabic_delete_empty_fails(self):
        result = self.dispatcher.dispatch("احذف ")
        self.assertFalse(result.success)

    def test_case_insensitive_run(self):
        result = self.dispatcher.dispatch("RUN ")
        self.assertFalse(result.success)

    def test_case_insensitive_list(self):
        result = self.dispatcher.dispatch("LIST")
        self.assertIsInstance(result, Result)


class CommandDispatcherOperationTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = CommandDispatcher(FakeServices())

    def test_create_empty_filename_fails(self):
        result = self.dispatcher.create("")
        self.assertFalse(result.success)

    def test_run_empty_filename_fails(self):
        result = self.dispatcher.run("")
        self.assertFalse(result.success)

    def test_read_empty_filename_fails(self):
        result = self.dispatcher.read("")
        self.assertFalse(result.success)

    def test_delete_empty_filename_fails(self):
        result = self.dispatcher.delete("")
        self.assertFalse(result.success)

    def test_write_empty_filename_fails(self):
        result = self.dispatcher.write("", "content")
        self.assertFalse(result.success)

    def test_append_empty_filename_fails(self):
        result = self.dispatcher.append("", "content")
        self.assertFalse(result.success)

    def test_create_project_empty_name_fails(self):
        result = self.dispatcher.create_project("")
        self.assertFalse(result.success)

    def test_list_returns_result(self):
        result = self.dispatcher.list()
        self.assertIsInstance(result, Result)

    def test_list_projects_returns_result(self):
        result = self.dispatcher.list_projects()
        self.assertIsInstance(result, Result)


class CommandDispatcherSuccessPathTests(unittest.TestCase):
    """Tests for successful command dispatch through file operations."""

    def setUp(self):
        self.dispatcher = CommandDispatcher(FakeServices())
        self.test_dir = os.path.join(os.path.dirname(__file__), "_cd_test_files")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_dispatches_with_content(self):
        path = os.path.join(self.test_dir, "w1.txt")
        result = self.dispatcher.dispatch(f"write {path} | hello world")
        self.assertTrue(result.success)

    def test_append_dispatches_with_content(self):
        path = os.path.join(self.test_dir, "a1.txt")
        self.dispatcher.dispatch(f"write {path} | first")
        result = self.dispatcher.dispatch(f"append {path} | second")
        self.assertTrue(result.success)
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("first", content)
        self.assertIn("second", content)

    def test_read_dispatches(self):
        path = os.path.join(self.test_dir, "r1.txt")
        with open(path, "w") as f:
            f.write("readable content")
        result = self.dispatcher.dispatch(f"read {path}")
        self.assertTrue(result.success)
        self.assertIn("readable content", str(result.data))

    def test_delete_dispatches(self):
        path = os.path.join(self.test_dir, "d1.txt")
        with open(path, "w") as f:
            f.write("to delete")
        result = self.dispatcher.dispatch(f"delete {path}")
        self.assertTrue(result.success)
        self.assertFalse(os.path.exists(path))

    def test_create_file_dispatches(self):
        path = os.path.join(self.test_dir, "c1.txt")
        result = self.dispatcher.dispatch(f"create file {path}")
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(path))
        if os.path.exists(path):
            os.remove(path)

    def test_run_dispatches_nonempty(self):
        result = self.dispatcher.dispatch("run nonexistent.py")
        self.assertIsInstance(result, Result)

    def test_write_with_multiple_pipes(self):
        path = os.path.join(self.test_dir, "mp1.txt")
        result = self.dispatcher.dispatch(f"write {path} | a|b|c")
        self.assertTrue(result.success)
        with open(path, "r") as f:
            content = f.read()
        self.assertIn("a|b|c", content)

    def test_write_dispatched_result_is_result(self):
        path = os.path.join(self.test_dir, "res1.txt")
        result = self.dispatcher.dispatch(f"write {path} | test")
        self.assertIsInstance(result, Result)

    def test_list_returns_workspace_files(self):
        result = self.dispatcher.list()
        self.assertTrue(result.success)

    def test_create_project_success(self):
        result = self.dispatcher.create_project("my_project")
        self.assertTrue(result.success)

    def test_list_projects_success(self):
        result = self.dispatcher.list_projects()
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
