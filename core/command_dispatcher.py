"""
core/command_dispatcher.py

Central dispatcher responsible for translating commands
into service operations.

CommandDispatcher does not implement business logic.
It only selects and invokes the appropriate service.
"""

from __future__ import annotations

from core.result import Result
from tools.file_tools import FileTools
from tools.python_tools import PythonTools


class CommandDispatcher:
    """
    Routes supported commands to the registered services.

    The dispatcher is the single entry point between Agents
    and the Services layer.
    """

    def __init__(self, services):
        self.services = services

        self.file_tools = FileTools()
        self.python_tools = PythonTools()
        self.project_manager = services.get("project_manager")

    # --------------------------------------------------
    # Public command interface
    # --------------------------------------------------

    def dispatch(self, command: str) -> Result:
        """
        Dispatch a raw command to the appropriate operation.
        """

        if not isinstance(command, str):
            return Result.fail(
                message="الأمر يجب أن يكون نصًا."
            )

        command = command.strip()

        if not command:
            return Result.fail(
                message="الأمر فارغ."
            )

        lower = command.lower()

        # --------------------------------------------------
        # Create file
        # --------------------------------------------------

        if lower.startswith("create file "):
            filename = command[len("create file "):].strip()
            return self.create(filename)

        if command.startswith("أنشئ ملف"):
            filename = command.replace("أنشئ ملف", "", 1).strip()
            return self.create(filename)

        # --------------------------------------------------
        # Run file
        # --------------------------------------------------

        if lower.startswith("run "):
            filename = command[len("run "):].strip()
            return self.run(filename)

        if command.startswith("شغل"):
            filename = command.replace("شغل", "", 1).strip()
            return self.run(filename)

        # --------------------------------------------------
        # List files
        # --------------------------------------------------

        if lower == "list":
            return self.list()

        # --------------------------------------------------
        # Read file
        # --------------------------------------------------

        if lower.startswith("read "):
            filename = command[len("read "):].strip()
            return self.read(filename)

        if command.startswith("اقرأ"):
            filename = command.replace("اقرأ", "", 1).strip()
            return self.read(filename)

        # --------------------------------------------------
        # Delete file
        # --------------------------------------------------

        if lower.startswith("delete "):
            filename = command[len("delete "):].strip()
            return self.delete(filename)

        if command.startswith("احذف"):
            filename = command.replace("احذف", "", 1).strip()
            return self.delete(filename)

        # --------------------------------------------------
        # Write file
        #
        # Syntax:
        # write file.py | content
        # --------------------------------------------------

        if lower.startswith("write "):
            body = command[len("write "):]

            if "|" not in body:
                return Result.fail(
                    message="الصيغة الصحيحة: write file.py | المحتوى"
                )

            filename, content = body.split("|", 1)

            return self.write(
                filename.strip(),
                content.lstrip(),
            )

        # --------------------------------------------------
        # Append file
        #
        # Syntax:
        # append file.py | content
        # --------------------------------------------------

        if lower.startswith("append "):
            body = command[len("append "):]

            if "|" not in body:
                return Result.fail(
                    message="الصيغة الصحيحة: append file.py | المحتوى"
                )

            filename, content = body.split("|", 1)

            return self.append(
                filename.strip(),
                content.lstrip(),
            )

        # --------------------------------------------------
        # Create project
        # --------------------------------------------------

        if lower.startswith("create project "):
            name = command[len("create project "):].strip()
            return self.create_project(name)

        # --------------------------------------------------
        # List projects
        # --------------------------------------------------

        if lower == "list projects":
            return self.list_projects()

        return Result.fail(
            message="الأمر غير مدعوم."
        )

    # --------------------------------------------------
    # File operations
    # --------------------------------------------------

    def create(self, filename: str) -> Result:
        if not filename:
            return Result.fail(
                message="يجب تحديد اسم الملف."
            )

        return self.file_tools.write_text(filename, "")

    def run(self, filename: str) -> Result:
        if not filename:
            return Result.fail(
                message="يجب تحديد اسم الملف."
            )

        return self.python_tools.run_script(filename)

    def list(self) -> Result:
        return self.file_tools.list_files("workspace")

    def read(self, filename: str) -> Result:
        if not filename:
            return Result.fail(
                message="يجب تحديد اسم الملف."
            )

        return self.file_tools.read_text(filename)

    def delete(self, filename: str) -> Result:
        if not filename:
            return Result.fail(
                message="يجب تحديد اسم الملف."
            )

        return self.file_tools.delete(filename)

    def write(self, filename: str, content: str) -> Result:
        if not filename:
            return Result.fail(
                message="يجب تحديد اسم الملف."
            )

        return self.file_tools.write_text(
            filename,
            content,
        )

    def append(self, filename: str, content: str) -> Result:
        if not filename:
            return Result.fail(
                message="يجب تحديد اسم الملف."
            )

        return self.file_tools.append_text(
            filename,
            content,
        )

    # --------------------------------------------------
    # Project operations
    # --------------------------------------------------

    def create_project(self, name: str) -> Result:
        if not name:
            return Result.fail(
                message="يجب تحديد اسم المشروع."
            )

        return self.project_manager.create_project(name)

    def list_projects(self) -> Result:
        return self.project_manager.list_projects()