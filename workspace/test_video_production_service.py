import unittest

from core.result import Result
from services.video_production_service import VideoProductionService


PLAN = {
    "timeline": [
        {
            "id": "growth",
            "duration": 10,
            "scenes": [
                {
                    "id": "seed",
                    "motion": {"event": "germinate"},
                    "camera": {"shot": "close"},
                    "audio": {"track": "nature"},
                    "continuity": {"previous": None},
                }
            ],
        }
    ]
}


class FakeInterpreter:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def interpret(self, instruction):
        self.calls.append(instruction)
        if self.error is not None:
            raise self.error
        return self.result


class VideoProductionServiceTests(unittest.TestCase):
    def test_construction_and_missing_interpreter(self):
        self.assertIsInstance(VideoProductionService(), VideoProductionService)
        result = VideoProductionService().create_plan("seed grows")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No video interpreter is registered.")

    def test_success_validates_temporal_plan(self):
        interpreter = FakeInterpreter(Result.ok(data=PLAN))
        result = VideoProductionService(interpreter).create_plan(" seed grows ")
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["stage_count"], 1)
        self.assertEqual(result.metadata["scene_count"], 1)
        self.assertEqual(interpreter.calls, ["seed grows"])

    def test_invalid_instruction_and_missing_temporal_fields_fail(self):
        self.assertFalse(
            VideoProductionService(FakeInterpreter(Result.ok(data=PLAN))).create_plan("").success
        )
        malformed = {"timeline": [{"id": "stage", "duration": 1, "scenes": []}]}
        result = VideoProductionService(
            FakeInterpreter(Result.ok(data=malformed))
        ).create_plan("instruction")
        self.assertFalse(result.success)

    def test_interpreter_failure_and_exception_are_normalized(self):
        failed = VideoProductionService(
            FakeInterpreter(Result.fail("private detail"))
        ).create_plan("instruction")
        errored = VideoProductionService(
            FakeInterpreter(error=RuntimeError("private detail"))
        ).create_plan("instruction")
        self.assertEqual(failed.message, "Video interpreter failed.")
        self.assertEqual(errored.message, "Video interpreter execution failed.")
        self.assertNotIn("private detail", repr(errored))


if __name__ == "__main__":
    unittest.main()
