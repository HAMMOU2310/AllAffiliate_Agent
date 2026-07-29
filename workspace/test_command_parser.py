from core.command_parser import CommandParser

parser = CommandParser()

task = parser.parse("اكتب برنامج بايثون")

print(task.task_type)
print(task.command)