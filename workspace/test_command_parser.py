import unittest

from core.command_parser import CommandParser


class CommandParserContractTests(unittest.TestCase):
    def test_existing_coding_command_remains_coding_task(self):
        task = CommandParser().parse("write example.py | print('ok')")
        self.assertEqual(task.task_type, "coding")

    def test_arabic_control_command_is_supported_for_coding(self):
        task = CommandParser().parse("\u0623\u0646\u0634\u0626 \u0645\u0644\u0641 example.py")
        self.assertEqual(task.task_type, "coding")


if __name__ == "__main__":
    unittest.main()
