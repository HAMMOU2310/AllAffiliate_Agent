"""Agent-level delegation for browser workflows."""
from __future__ import annotations

from typing import Any

from core.base_agent import BaseAgent
from core.result import Result

_SEARCH_PREFIXES = ("search ", "abcht ", "\u0627\u0628\u062d\u062b ", "\u0628\u062d\u062b ")
_INSPECT_PREFIXES = ("inspect ", "\u062a\u062d\u0642\u0642 ")


class BrowserAgent(BaseAgent):
    name = "Browser Agent"
    task_type = "browser"

    def __init__(self, services):
        self.browser = services.get("browser_service")

    def execute(self, task) -> Result:
        if self.browser is None:
            return Result.fail("Browser service is not registered.")

        command = getattr(task, "command", "")
        if not isinstance(command, str):
            return Result.fail("Browser command is invalid.")

        operation, payload = self._parse_command(command)

        return self.browser.execute(operation, payload)

    @staticmethod
    def _parse_command(command: str) -> tuple[str, Any]:
        lower = command.strip().lower()

        for prefix in _SEARCH_PREFIXES:
            if lower.startswith(prefix):
                query = command.strip()[len(prefix):].strip()
                return "extract", query

        for prefix in _INSPECT_PREFIXES:
            if lower.startswith(prefix):
                query = command.strip()[len(prefix):].strip()
                return "inspect", query

        return "execute_workflow", command
