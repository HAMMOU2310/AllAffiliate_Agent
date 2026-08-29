"""Task-level delegation for service-only capabilities."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.base_agent import BaseAgent
from core.result import Result


class CapabilityAgent(BaseAgent):
    """Delegate one task type to one existing Service method."""

    _STRING_TASKS = {"research", "video", "audio"}

    def __init__(
        self,
        services,
        task_type: str,
        service_name: str,
        method_name: str,
    ) -> None:
        self.task_type = task_type
        self.name = f"{task_type.title()} Capability Agent"
        self._services = services
        self._service_name = service_name
        self._method_name = method_name

    def execute(self, task) -> Result:
        service = self._services.get(self._service_name)
        if service is None:
            return Result.fail("Capability service is not registered.")

        method = getattr(service, self._method_name, None)
        if not callable(method):
            return Result.fail("Capability service method is invalid.")

        data = getattr(task, "data", None)
        payload = data.get("payload") if isinstance(data, Mapping) else None
        command = getattr(task, "command", "")

        try:
            if isinstance(payload, Mapping):
                result = method(**dict(payload))
            elif self.task_type in self._STRING_TASKS:
                body = self._command_body(command)
                if not body:
                    return Result.fail("Capability command input is invalid.")
                result = method(body)
            else:
                return Result.fail("Capability payload is required.")
        except Exception:
            return Result.fail("Capability service execution failed.")

        if not isinstance(result, Result):
            return Result.fail("Capability service returned an invalid Result.")
        return result

    def _command_body(self, command: Any) -> str:
        if not isinstance(command, str):
            return ""
        prefix = f"{self.task_type} "
        if command.lower().startswith(prefix):
            return command[len(prefix):].strip()
        return command.strip()
