"""Agent-level delegation for browser workflows."""
from core.base_agent import BaseAgent
from core.result import Result


class BrowserAgent(BaseAgent):
    name = "Browser Agent"
    task_type = "browser"

    def __init__(self, services):
        self.browser = services.get("browser_service")

    def execute(self, task) -> Result:
        return self.browser.execute("execute_workflow", task.command)
