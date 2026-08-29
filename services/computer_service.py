"""Permission-gated computer automation boundary."""
from __future__ import annotations
from typing import Any, Protocol
from core.result import Result


class ComputerAdapter(Protocol):
    def execute(self, operation: str, payload: Any = None) -> Result: ...


class ComputerService:
    _OPERATIONS = {"keyboard", "mouse", "window", "application", "screen", "verify_state"}

    def __init__(self, adapter: ComputerAdapter | None = None, permitted: bool = False) -> None:
        self._adapter = adapter
        self._permitted = permitted

    def execute(self, operation: str, payload: Any = None) -> Result:
        if not self._permitted:
            return Result.fail("Computer operation requires explicit permission.")
        if not isinstance(operation, str) or operation.strip().lower() not in self._OPERATIONS:
            return Result.fail("Computer operation is invalid.")
        if self._adapter is None:
            return Result.fail("No computer adapter is registered.")
        execute = getattr(self._adapter, "execute", None)
        if not callable(execute):
            return Result.fail("Computer adapter is invalid.")
        try:
            result = execute(operation.strip().lower(), payload)
        except Exception:
            return Result.fail("Computer adapter execution failed.")
        if not isinstance(result, Result):
            return Result.fail("Computer adapter returned an invalid Result.")
        return result
