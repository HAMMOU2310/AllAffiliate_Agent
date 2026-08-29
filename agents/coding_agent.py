"""
agents/coding_agent.py

Agent responsible for coding-related tasks.

CodingAgent does not execute commands directly.
It forwards the task command to CommandDispatcher.
"""

from core.base_agent import BaseAgent
from core.result import Result


class CodingAgent(BaseAgent):
    """
    Agent responsible for coding-related tasks.
    """

    name = "Coding Agent"
    task_type = "coding"

    def __init__(self, services):
        self.dispatcher = services.get("command_dispatcher")

    def execute(self, task) -> Result:
        return self.dispatcher.dispatch(task.command)