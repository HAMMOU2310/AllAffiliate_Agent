from core.command_parser import CommandParser
from core.task import Task


class TaskManager:

    def __init__(self):

        self.parser = CommandParser()

    def create_task(self, command: str) -> Task:

        return self.parser.parse(command)