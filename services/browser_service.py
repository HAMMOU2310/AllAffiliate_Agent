"""Safe, provider-neutral browser service boundary."""
from __future__ import annotations
from typing import Any, Protocol
from core.result import Result


class BrowserAdapter(Protocol):
    def execute(self, operation: str, payload: Any = None) -> Result: ...


class BrowserService:
    _OPERATIONS = {"navigate", "inspect", "extract", "interact", "validate", "execute_workflow"}

    def __init__(self, adapter: BrowserAdapter | None = None) -> None:
        self._adapter = adapter

    def execute(self, operation: str, payload: Any = None) -> Result:
        if not isinstance(operation, str) or operation.strip().lower() not in self._OPERATIONS:
            return Result.fail("Browser operation is invalid.")
        if self._adapter is None:
            return Result.fail("No browser adapter is registered.")
        execute = getattr(self._adapter, "execute", None)
        if not callable(execute):
            return Result.fail("Browser adapter is invalid.")
        try:
            result = execute(operation.strip().lower(), payload)
        except Exception:
            return Result.fail("Browser adapter execution failed.")
        if not isinstance(result, Result):
            return Result.fail("Browser adapter returned an invalid Result.")
        return result if not result.success else Result.ok(
            data=result.data, message="Browser operation completed.", metadata=result.metadata
        )
