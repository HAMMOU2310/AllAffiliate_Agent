import unittest

from core.result import Result
from services.audio_service import AudioService


PLAN = {
    "tracks": [
        {
            "id": "narration",
            "start": 0,
            "duration": 3,
            "kind": "voice",
            "continuity": {"previous": None},
        }
    ]
}


class FakeInterpreter:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def interpret(self, instruction):
        if self.error is not None:
            raise self.error
        return self.result


class AudioServiceTests(unittest.TestCase):
    def test_construction_and_missing_interpreter(self):
        self.assertIsInstance(AudioService(), AudioService)
        self.assertFalse(AudioService().create_plan("voice").success)

    def test_success_normalizes_tracks(self):
        result = AudioService(FakeInterpreter(Result.ok(data=PLAN))).create_plan(" voice ")
        self.assertTrue(result.success)
        self.assertEqual(result.data["tracks"][0]["start"], 0.0)

    def test_invalid_and_duplicate_tracks_fail(self):
        malformed = {"tracks": [{"id": "x", "start": 0, "duration": 1, "kind": "voice"}]}
        duplicate = {"tracks": [
            {"id": "x", "start": 0, "duration": 1, "kind": "voice", "continuity": {}},
            {"id": "x", "start": 1, "duration": 1, "kind": "voice", "continuity": {}},
        ]}
        self.assertFalse(AudioService(FakeInterpreter(Result.ok(data=malformed))).create_plan("x").success)
        self.assertFalse(AudioService(FakeInterpreter(Result.ok(data=duplicate))).create_plan("x").success)

    def test_failure_and_exception_are_normalized(self):
        failed = AudioService(FakeInterpreter(Result.fail("private"))).create_plan("x")
        errored = AudioService(FakeInterpreter(error=RuntimeError("private"))).create_plan("x")
        self.assertEqual(failed.message, "Audio interpreter failed.")
        self.assertEqual(errored.message, "Audio interpreter execution failed.")


if __name__ == "__main__":
    unittest.main()
