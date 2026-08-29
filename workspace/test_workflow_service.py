import unittest

from core.result import Result
from services.workflow_service import WorkflowService


class FakePlanner:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def plan(self, goal, context=None):
        self.calls.append((goal, context))
        if self.error is not None:
            raise self.error
        return self.result


STEPS = [
    {"id": "research", "description": "Research the goal", "status": "ready"},
    {"id": "report", "description": "Prepare a report", "status": "PENDING"},
]


class WorkflowServiceTests(unittest.TestCase):
    def test_construction_and_missing_planner(self):
        self.assertIsInstance(WorkflowService(), WorkflowService)
        result = WorkflowService().plan("goal")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No workflow planner is registered.")

    def test_success_normalizes_order_and_status(self):
        planner = FakePlanner(Result.ok(data=STEPS))
        result = WorkflowService(planner).plan("goal", {"priority": "high"})
        self.assertTrue(result.success)
        self.assertEqual([step["id"] for step in result.data], ["research", "report"])
        self.assertEqual(result.data[0]["status"], "READY")
        self.assertEqual(planner.calls[0], ("goal", {"priority": "high"}))

    def test_invalid_goal_and_context_fail(self):
        planner = FakePlanner(Result.ok(data=[]))
        service = WorkflowService(planner)
        self.assertFalse(service.plan("").success)
        self.assertFalse(service.plan("goal", context=[]).success)

    def test_malformed_steps_duplicate_ids_and_status_fail(self):
        cases = [
            [{"id": "x", "description": "", "status": "READY"}],
            [
                {"id": "x", "description": "one", "status": "READY"},
                {"id": "x", "description": "two", "status": "READY"},
            ],
            [{"id": "x", "description": "one", "status": "UNKNOWN"}],
        ]
        for steps in cases:
            result = WorkflowService(FakePlanner(Result.ok(data=steps))).plan("goal")
            self.assertFalse(result.success)

    def test_planner_failure_and_exception_are_normalized(self):
        failed = WorkflowService(FakePlanner(Result.fail("private detail"))).plan("goal")
        errored = WorkflowService(
            FakePlanner(error=RuntimeError("private detail"))
        ).plan("goal")
        self.assertEqual(failed.message, "Workflow planner failed.")
        self.assertEqual(errored.message, "Workflow planner execution failed.")
        self.assertNotIn("private detail", repr(errored))


if __name__ == "__main__":
    unittest.main()
