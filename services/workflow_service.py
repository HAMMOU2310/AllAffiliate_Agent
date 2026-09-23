"""Provider-neutral workflow planning and execution boundary."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


class WorkflowPlanner(Protocol):
    """Optional injected planner boundary."""

    def plan(self, goal: str, context: dict[str, Any] | None = None) -> Result:
        ...


class WorkflowService:
    """Validate and execute ordered workflows.

    Planning: validates plan structure via an injected WorkflowPlanner.
    Execution: runs valid steps sequentially through a TaskRouter,
    collecting per-step Results and returning an aggregate Result.
    """

    _STATUSES = {"PENDING", "READY", "BLOCKED", "COMPLETED"}

    def __init__(self, planner: WorkflowPlanner | None = None, router: Any | None = None) -> None:
        self._planner = planner
        self._router = router

    # ------------------------------------------------------------------
    # Planning (unchanged public API)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        steps: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
        stop_on_failure: bool = True,
    ) -> Result:
        """Execute a validated workflow sequentially.

        Each step must contain:
            id (str)           — unique step identifier
            task_type (str)    — target agent task type
            command (str)      — command string for the task
            data (dict)        — optional task data payload

        Args:
            steps: Normalized workflow steps.
            context: Optional shared context passed to every step's data.
            stop_on_failure: If True, halt on first failure.

        Returns:
            Result with aggregated execution data.
        """
        if not isinstance(steps, list) or not steps:
            return Result.fail("Workflow has no steps to execute.")

        if self._router is None:
            return Result.fail("No task router registered for workflow execution.")

        validation_error = self._validate_executable_steps(steps)
        if validation_error:
            return Result.fail(validation_error)

        step_results: list[dict[str, Any]] = []
        completed = 0
        failed = 0
        failed_step_id = None

        for step in steps:
            step_id = step["id"]
            task_type = step["task_type"]
            command = step.get("command", "")
            step_data = dict(step.get("data", {}))

            if context:
                step_data["context"] = context

            from core.task import Task

            task = Task(
                task_type=task_type,
                command=command,
                data=step_data,
            )

            try:
                result = self._router.route(task)
            except Exception as exc:
                result = Result.fail(
                    message=f"Step execution raised an exception: {exc}",
                    errors=[str(exc)],
                )

            step_record = {
                "id": step_id,
                "task_type": task_type,
                "success": result.success,
                "message": result.message,
                "data": result.data,
                "errors": result.errors,
            }
            step_results.append(step_record)

            if result.success:
                completed += 1
            else:
                failed += 1
                if failed_step_id is None:
                    failed_step_id = step_id
                if stop_on_failure:
                    break

        total = len(steps)
        all_succeeded = failed == 0

        if all_succeeded:
            message = f"Workflow completed: {completed}/{total} steps succeeded."
        elif stop_on_failure:
            message = f"Workflow halted at step '{failed_step_id}': {completed} completed, {failed} failed."
        else:
            message = f"Workflow finished: {completed}/{total} succeeded, {failed} failed."

        return Result.ok(
            data={
                "steps": step_results,
                "completed": completed,
                "failed": failed,
                "total": total,
                "all_succeeded": all_succeeded,
                "stop_on_failure": stop_on_failure,
            },
            message=message,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_executable_steps(self, steps: list[dict[str, Any]]) -> str | None:
        """Return an error message if steps are invalid for execution, else None."""
        seen_ids: set[str] = set()
        for step in steps:
            if not isinstance(step, Mapping):
                return "Workflow step is not a valid mapping."

            step_id = step.get("id")
            if not isinstance(step_id, str) or not step_id.strip():
                return "Workflow step missing a valid id."
            step_id = step_id.strip()

            if step_id in seen_ids:
                return f"Duplicate workflow step id: '{step_id}'."
            seen_ids.add(step_id)

            task_type = step.get("task_type")
            if not isinstance(task_type, str) or not task_type.strip():
                return f"Step '{step_id}' missing a valid task_type."

        return None

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
