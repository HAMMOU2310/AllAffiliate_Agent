"""Provider-neutral workflow planning boundary for v0.8."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


class WorkflowPlanner(Protocol):
    """Optional injected planner boundary."""

    def plan(self, goal: str, context: dict[str, Any] | None = None) -> Result:
        ...


class WorkflowService:
    """Validate ordered plans without executing their steps."""

    _STATUSES = {"PENDING", "READY", "BLOCKED", "COMPLETED"}

    def __init__(self, planner: WorkflowPlanner | None = None) -> None:
        self._planner = planner

    def plan(
        self,
        goal: str,
        context: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(goal, str) or not goal.strip():
            return Result.fail("Workflow goal is invalid.")

        if context is not None and not isinstance(context, dict):
            return Result.fail("Workflow context is invalid.")

        if self._planner is None:
            return Result.fail("No workflow planner is registered.")

        planner = getattr(self._planner, "plan", None)
        if not callable(planner):
            return Result.fail("Workflow planner is invalid.")

        try:
            result = planner(goal.strip(), context)
        except Exception:
            return Result.fail("Workflow planner execution failed.")

        if not isinstance(result, Result) or not result.success:
            return Result.fail("Workflow planner failed.")

        steps = self._normalize_steps(result.data)
        if steps is None:
            return Result.fail("Workflow planner returned a malformed plan.")

        return Result.ok(
            data=steps,
            message="Workflow plan validated successfully.",
            metadata={
                "goal": goal.strip(),
                "step_count": len(steps),
            },
        )

    @classmethod
    def _normalize_steps(cls, steps: Any) -> list[dict[str, Any]] | None:
        if isinstance(steps, (str, bytes, Mapping)) or not isinstance(
            steps, Sequence
        ):
            return None

        normalized: list[dict[str, Any]] = []
        identifiers: set[str] = set()
        for step in steps:
            if not isinstance(step, Mapping):
                return None

            identifier = step.get("id")
            description = step.get("description")
            status = step.get("status")
            if not isinstance(identifier, str) or not identifier.strip():
                return None
            if identifier.strip() in identifiers:
                return None
            if not isinstance(description, str) or not description.strip():
                return None
            if not isinstance(status, str) or status.strip().upper() not in cls._STATUSES:
                return None

            identifiers.add(identifier.strip())
            item = dict(step)
            item["id"] = identifier.strip()
            item["description"] = description.strip()
            item["status"] = status.strip().upper()
            normalized.append(item)

        return normalized
