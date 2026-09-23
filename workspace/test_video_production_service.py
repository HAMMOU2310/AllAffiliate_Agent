import json
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


class FakeGenerator:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.last_prompt = None
        self.last_params = None

    def generate(self, prompt, parameters=None):
        self.last_prompt = prompt
        self.last_params = parameters
        if self.error is not None:
            raise self.error
        return self.result


class FakeRenderer:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.last_plan = None
        self.last_params = None

    def render(self, plan, parameters=None):
        self.last_plan = plan
        self.last_params = parameters
        if self.error is not None:
            raise self.error
        return self.result


# --------------------------------------------------
# Construction
# --------------------------------------------------


class VideoProductionServiceConstructionTests(unittest.TestCase):
    def test_default_construction(self):
        svc = VideoProductionService()
        self.assertIsInstance(svc, VideoProductionService)

    def test_construction_with_all_providers(self):
        svc = VideoProductionService(
            interpreter=FakeInterpreter(),
            generator=FakeGenerator(),
            renderer=FakeRenderer(),
        )
        self.assertIsInstance(svc, VideoProductionService)


# --------------------------------------------------
# Execute dispatch
# --------------------------------------------------


class VideoProductionServiceExecuteTests(unittest.TestCase):
    def test_execute_generate(self):
        gen = FakeGenerator(result=Result.ok(data={"path": "/tmp/v.mp4"}))
        svc = VideoProductionService(generator=gen)
        result = svc.execute("generate a sunset timelapse")
        self.assertTrue(result.success)

    def test_execute_render(self):
        rnd = FakeRenderer(result=Result.ok(data={"path": "/tmp/rendered.mp4"}))
        svc = VideoProductionService(renderer=rnd)
        result = svc.execute("render " + json.dumps(PLAN))
        self.assertTrue(result.success)

    def test_execute_create_plan(self):
        interp = FakeInterpreter(Result.ok(data=PLAN))
        svc = VideoProductionService(interpreter=interp)
        result = svc.execute("create_plan seed grows")
        self.assertTrue(result.success)

    def test_execute_unsupported_operation(self):
        svc = VideoProductionService()
        result = svc.execute("download video")
        self.assertFalse(result.success)
        self.assertIn("Unsupported video operation", result.message)

    def test_execute_empty_command(self):
        svc = VideoProductionService()
        self.assertFalse(svc.execute("").success)
        self.assertFalse(svc.execute(None).success)


# --------------------------------------------------
# Generate
# --------------------------------------------------


class VideoProductionServiceGenerateTests(unittest.TestCase):
    def test_generate_success(self):
        gen = FakeGenerator(
            result=Result.ok(
                data={"path": "/tmp/v.mp4", "format": "mp4", "duration": 5.0},
                message="Video generated.",
            )
        )
        svc = VideoProductionService(generator=gen)
        result = svc.generate("a cat playing piano")
        self.assertTrue(result.success)
        self.assertEqual(gen.last_prompt, "a cat playing piano")

    def test_generate_with_parameters(self):
        gen = FakeGenerator(result=Result.ok(data={"path": "/tmp/v.mp4"}))
        svc = VideoProductionService(generator=gen)
        params = {"duration": 10, "resolution": "1080p"}
        result = svc.generate("sunset", parameters=params)
        self.assertTrue(result.success)
        self.assertEqual(gen.last_params, params)

    def test_generate_empty_prompt(self):
        svc = VideoProductionService(generator=FakeGenerator())
        self.assertFalse(svc.generate("").success)
        self.assertFalse(svc.generate("   ").success)
        self.assertFalse(svc.generate(None).success)

    def test_generate_no_provider(self):
        svc = VideoProductionService()
        result = svc.generate("test")
        self.assertFalse(result.success)
        self.assertIn("video generation provider", result.message.lower())

    def test_generate_invalid_provider(self):
        svc = VideoProductionService(generator="not_a_provider")
        result = svc.generate("test")
        self.assertFalse(result.success)

    def test_generate_provider_failure(self):
        gen = FakeGenerator(result=Result.fail("quota exceeded"))
        svc = VideoProductionService(generator=gen)
        result = svc.generate("test")
        self.assertFalse(result.success)

    def test_generate_provider_exception(self):
        gen = FakeGenerator(error=RuntimeError("api down"))
        svc = VideoProductionService(generator=gen)
        result = svc.generate("test")
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    def test_generate_invalid_result_type(self):
        gen = FakeGenerator(result="not_a_result")
        svc = VideoProductionService(generator=gen)
        result = svc.generate("test")
        self.assertFalse(result.success)


# --------------------------------------------------
# Render
# --------------------------------------------------


class VideoProductionServiceRenderTests(unittest.TestCase):
    def test_render_success_dict(self):
        rnd = FakeRenderer(
            result=Result.ok(
                data={"path": "/tmp/rendered.mp4", "format": "mp4"},
                message="Render complete.",
            )
        )
        svc = VideoProductionService(renderer=rnd)
        result = svc.render(PLAN)
        self.assertTrue(result.success)
        self.assertEqual(rnd.last_plan, PLAN)

    def test_render_success_json_string(self):
        rnd = FakeRenderer(result=Result.ok(data={"path": "/tmp/rendered.mp4"}))
        svc = VideoProductionService(renderer=rnd)
        result = svc.render(json.dumps(PLAN))
        self.assertTrue(result.success)
        self.assertEqual(rnd.last_plan, PLAN)

    def test_render_with_parameters(self):
        rnd = FakeRenderer(result=Result.ok(data={"path": "/tmp/v.mp4"}))
        svc = VideoProductionService(renderer=rnd)
        params = {"quality": "high"}
        result = svc.render(PLAN, parameters=params)
        self.assertTrue(result.success)
        self.assertEqual(rnd.last_params, params)

    def test_render_empty_plan(self):
        svc = VideoProductionService(renderer=FakeRenderer())
        self.assertFalse(svc.render("").success)
        self.assertFalse(svc.render("   ").success)

    def test_render_invalid_json_string(self):
        svc = VideoProductionService(renderer=FakeRenderer())
        result = svc.render("not valid json {{{")
        self.assertFalse(result.success)
        self.assertIn("not valid JSON", result.message)

    def test_render_non_dict_plan(self):
        svc = VideoProductionService(renderer=FakeRenderer())
        result = svc.render([1, 2, 3])
        self.assertFalse(result.success)

    def test_render_no_provider(self):
        svc = VideoProductionService()
        result = svc.render(PLAN)
        self.assertFalse(result.success)
        self.assertIn("video rendering provider", result.message.lower())

    def test_render_invalid_provider(self):
        svc = VideoProductionService(renderer="not_a_provider")
        result = svc.render(PLAN)
        self.assertFalse(result.success)

    def test_render_provider_failure(self):
        rnd = FakeRenderer(result=Result.fail("render timeout"))
        svc = VideoProductionService(renderer=rnd)
        result = svc.render(PLAN)
        self.assertFalse(result.success)

    def test_render_provider_exception(self):
        rnd = FakeRenderer(error=RuntimeError("gpu error"))
        svc = VideoProductionService(renderer=rnd)
        result = svc.render(PLAN)
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    def test_render_invalid_result_type(self):
        rnd = FakeRenderer(result={"not": "a result"})
        svc = VideoProductionService(renderer=rnd)
        result = svc.render(PLAN)
        self.assertFalse(result.success)


# --------------------------------------------------
# create_plan (legacy — preserved)
# --------------------------------------------------


class VideoProductionServiceCreatePlanTests(unittest.TestCase):
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
