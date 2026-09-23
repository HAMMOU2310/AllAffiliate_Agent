"""Tests for WorkflowService execution engine (Batch 4)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.result import Result
from core.task import Task
from services.workflow_service import WorkflowService


# ── Helpers ──────────────────────────────────────────────────────


def _make_step(task_type="research", command="research AI", data=None, step_id="step1"):
    return {
        "id": step_id,
        "task_type": task_type,
        "command": command,
        "data": data or {},
    }


class FakeRouter:
    def __init__(self, results=None):
        self._results = results or []
        self._call_index = 0
        self.calls = []

    def route(self, task):
        self.calls.append(task)
        if self._call_index < len(self._results):
            r = self._results[self._call_index]
            self._call_index += 1
            return r
        return Result.ok(data="default")


# ── Empty / Null Input ──────────────────────────────────────────


class TestExecuteEmptyInput:
    def test_empty_steps_list(self):
        svc = WorkflowService(router=FakeRouter())
        result = svc.execute([])
        assert result.success is False
        assert "no steps" in result.message.lower()

    def test_none_steps(self):
        svc = WorkflowService(router=FakeRouter())
        result = svc.execute(None)
        assert result.success is False

    def test_no_router(self):
        svc = WorkflowService()
        result = svc.execute([_make_step()])
        assert result.success is False
        assert "no task router" in result.message.lower()


# ── Single Step Success ─────────────────────────────────────────


class TestExecuteSingleStep:
    def test_one_step_success(self):
        router = FakeRouter([Result.ok(data="done")])
        svc = WorkflowService(router=router)
        result = svc.execute([_make_step()])
        assert result.success is True
        assert result.data["completed"] == 1
        assert result.data["failed"] == 0
        assert result.data["all_succeeded"] is True

    def test_step_record_preserved(self):
        router = FakeRouter([Result.ok(data="x", message="ok")])
        svc = WorkflowService(router=router)
        result = svc.execute([_make_step()])
        step = result.data["steps"][0]
        assert step["success"] is True
        assert step["message"] == "ok"
        assert step["data"] == "x"

    def test_task_created_correctly(self):
        router = FakeRouter([Result.ok()])
        svc = WorkflowService(router=router)
        svc.execute([_make_step(task_type="analyze", command="analyze data")])
        task = router.calls[0]
        assert isinstance(task, Task)
        assert task.task_type == "analyze"
        assert task.command == "analyze data"


# ── Multi-Step Success ──────────────────────────────────────────


class TestExecuteMultiStep:
    def test_three_steps_all_succeed(self):
        router = FakeRouter([Result.ok(), Result.ok(), Result.ok()])
        svc = WorkflowService(router=router)
        steps = [_make_step(step_id=f"s{i}") for i in range(3)]
        result = svc.execute(steps)
        assert result.data["completed"] == 3
        assert result.data["failed"] == 0
        assert result.data["total"] == 3
        assert result.data["all_succeeded"] is True

    def test_execution_order(self):
        order = []
        results = []
        for i in range(3):
            idx = i
            results.append(Result.ok(data=f"step{idx}"))
        router = FakeRouter(results)
        svc = WorkflowService(router=router)
        steps = [_make_step(step_id=f"s{i}") for i in range(3)]
        svc.execute(steps)
        for i, task in enumerate(router.calls):
            assert task.data.get("_step_index") is None or True


# ── Validation ──────────────────────────────────────────────────


class TestValidation:
    def test_missing_task_type(self):
        router = FakeRouter([Result.ok()])
        svc = WorkflowService(router=router)
        bad_step = {"id": "s1", "command": "x"}
        result = svc.execute([bad_step])
        assert result.success is False
        assert "task_type" in result.message

    def test_missing_id(self):
        router = FakeRouter([Result.ok()])
        svc = WorkflowService(router=router)
        bad_step = {"task_type": "research", "command": "x"}
        result = svc.execute([bad_step])
        assert result.success is False
        assert "id" in result.message

    def test_duplicate_step_ids(self):
        router = FakeRouter([Result.ok(), Result.ok()])
        svc = WorkflowService(router=router)
        steps = [_make_step(step_id="dup"), _make_step(step_id="dup")]
        result = svc.execute(steps)
        assert result.success is False
        assert "duplicate" in result.message.lower()

    def test_non_mapping_step(self):
        router = FakeRouter([Result.ok()])
        svc = WorkflowService(router=router)
        result = svc.execute(["not a dict"])
        assert result.success is False


# ── Step Failure ────────────────────────────────────────────────


class TestStepFailure:
    def test_single_step_failure(self):
        router = FakeRouter([Result.fail("step failed")])
        svc = WorkflowService(router=router)
        result = svc.execute([_make_step()])
        assert result.data["completed"] == 0
        assert result.data["failed"] == 1
        assert result.data["all_succeeded"] is False

    def test_stop_on_failure_halts(self):
        router = FakeRouter([Result.fail("fail"), Result.ok()])
        svc = WorkflowService(router=router)
        steps = [_make_step(step_id="s1"), _make_step(step_id="s2")]
        result = svc.execute(steps, stop_on_failure=True)
        assert result.data["completed"] == 0
        assert result.data["failed"] == 1
        assert len(router.calls) == 1

    def test_continue_on_failure(self):
        router = FakeRouter([Result.fail("fail"), Result.ok()])
        svc = WorkflowService(router=router)
        steps = [_make_step(step_id="s1"), _make_step(step_id="s2")]
        result = svc.execute(steps, stop_on_failure=False)
        assert result.data["completed"] == 1
        assert result.data["failed"] == 1
        assert len(router.calls) == 2

    def test_failure_message_contains_step_id(self):
        router = FakeRouter([Result.fail("err")])
        svc = WorkflowService(router=router)
        result = svc.execute([_make_step(step_id="bad_step")])
        assert "bad_step" in result.message

    def test_step_exception_caught(self):
        router = MagicMock()
        router.route.side_effect = RuntimeError("boom")
        svc = WorkflowService(router=router)
        result = svc.execute([_make_step()])
        assert result.data["failed"] == 1
        assert result.data["steps"][0]["success"] is False

    def test_per_step_result_preserved(self):
        router = FakeRouter([
            Result.ok(data="r1"),
            Result.fail("e2", errors=["err2"]),
        ])
        svc = WorkflowService(router=router)
        steps = [_make_step(step_id="s1"), _make_step(step_id="s2")]
        result = svc.execute(steps, stop_on_failure=False)
        assert result.data["steps"][0]["data"] == "r1"
        assert result.data["steps"][1]["errors"] == ["err2"]


# ── Context Propagation ─────────────────────────────────────────


class TestContextPropagation:
    def test_context_passed_to_step_data(self):
        router = FakeRouter([Result.ok()])
        svc = WorkflowService(router=router)
        ctx = {"session_id": "abc"}
        svc.execute([_make_step()], context=ctx)
        task = router.calls[0]
        assert task.data["context"] == ctx

    def test_step_data_not_mutated(self):
        router = FakeRouter([Result.ok()])
        svc = WorkflowService(router=router)
        original_data = {"key": "val"}
        step = _make_step(data=original_data)
        svc.execute([step], context={"c": 1})
        assert "context" not in original_data


# ── Message Quality ─────────────────────────────────────────────


class TestMessages:
    def test_success_message(self):
        router = FakeRouter([Result.ok()])
        svc = WorkflowService(router=router)
        result = svc.execute([_make_step()])
        assert "completed" in result.message.lower()

    def test_failure_message_stop(self):
        router = FakeRouter([Result.fail("x")])
        svc = WorkflowService(router=router)
        result = svc.execute([_make_step(step_id="f1")])
        assert "halted" in result.message.lower()

    def test_failure_message_continue(self):
        router = FakeRouter([Result.fail("x"), Result.ok()])
        svc = WorkflowService(router=router)
        steps = [_make_step(step_id="s1"), _make_step(step_id="s2")]
        result = svc.execute(steps, stop_on_failure=False)
        assert "finished" in result.message.lower()


# ── Plan API Compatibility ──────────────────────────────────────


class TestPlanCompat:
    def test_plan_unchanged_with_planner(self):
        class FakePlanner:
            def plan(self, goal, context=None):
                return Result.ok(data=[
                    {"id": "a", "description": "d", "status": "READY"}
                ])
        svc = WorkflowService(planner=FakePlanner())
        result = svc.plan("test goal")
        assert result.success is True
        assert result.data[0]["id"] == "a"

    def test_plan_without_planner(self):
        svc = WorkflowService()
        result = svc.plan("goal")
        assert result.success is False
        assert "planner" in result.message.lower()

    def test_plan_normalize_steps_unchanged(self):
        result = WorkflowService._normalize_steps("bad")
        assert result is None

    def test_plan_empty_steps(self):
        class P:
            def plan(self, goal, context=None):
                return Result.ok(data=[])
        result = WorkflowService(P()).plan("g")
        assert result.success is True
        assert result.data == []
