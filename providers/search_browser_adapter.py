"""BrowserAdapter implementation that delegates search to OpenSERPSearchProvider."""

from __future__ import annotations

from typing import Any

from core.result import Result


class SearchBrowserAdapter:
    """Translate BrowserService search operations into OpenSERP searches."""

    _SEARCH_OPERATIONS = {"extract", "inspect"}

    def __init__(self, search_provider: Any) -> None:
        self._provider = search_provider

    def execute(self, operation: str, payload: Any = None) -> Result:
        if not isinstance(operation, str):
            return Result.fail("Browser operation is invalid.")

        op = operation.strip().lower()

        if op == "execute_workflow":
            return self._execute_search(payload)

        if op in self._SEARCH_OPERATIONS:
            return self._execute_search(payload)

        return Result.fail(
            f"Browser operation is not supported: {op}",
        )

    def _execute_search(self, payload: Any) -> Result:
        query, scope = self._extract_search_params(payload)

        if not query:
            return Result.fail("Browser search query is invalid.")

        search = getattr(self._provider, "search", None)
        if not callable(search):
            return Result.fail("Browser search provider is invalid.")

        try:
            result = search(query, scope)
        except Exception:
            return Result.fail("Browser search provider execution failed.")

        if not isinstance(result, Result):
            return Result.fail("Browser search provider returned an invalid Result.")

        return result

    @staticmethod
    def _extract_search_params(payload: Any) -> tuple[str, str | None]:
        if isinstance(payload, str):
            return payload.strip(), None

        if isinstance(payload, dict):
            query = payload.get("query") or payload.get("text") or ""
            scope = payload.get("scope")
            return str(query).strip(), scope if isinstance(scope, str) else None

        if isinstance(payload, list) and payload:
            first = payload[0]
            if isinstance(first, str):
                return first.strip(), None
            if isinstance(first, dict):
                query = first.get("query") or first.get("text") or ""
                scope = first.get("scope")
                return str(query).strip(), scope if isinstance(scope, str) else None

        return "", None
