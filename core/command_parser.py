from core.task import Task


class CommandParser:
    """
    يحول أمر المستخدم إلى Task.
    """

    def parse(self, command: str) -> Task:

        command = command.strip()
        lower = command.lower()

        task_type = "unknown"

        coding_keywords = (
            "برنامج",
            "بايثون",
            "python",
            "أنشئ مشروع",
            "انشئ مشروع",
            "create project",
            "create-project",
            "أنشئ ملف",
            "انشئ ملف",
            "ملف",
            "create file",
            "create python file",
        )

        if any(keyword.lower() in lower for keyword in coding_keywords):
            task_type = "coding"

        return Task(
            task_type=task_type,
            command=command,
        )