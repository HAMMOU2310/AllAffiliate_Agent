"""Agent-level delegation for permission-gated computer workflows."""
from core.base_agent import BaseAgent
from core.result import Result


class ComputerAgent(BaseAgent):
    name = "Computer Agent"
    task_type = "computer"

    def __init__(self, services):
        self.computer = services.get("computer_service")

    def execute(self, task) -> Result:
        return self.computer.execute("verify_state", task.command)
