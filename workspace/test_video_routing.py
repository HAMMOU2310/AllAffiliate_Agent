import json
import unittest

from core.result import Result
from core.task import Task
from core.command_parser import CommandParser
from core.router import TaskRouter
from agents.capability_agent import CapabilityAgent
from services.video_production_service import VideoProductionService


PLAN = {
    "timeline": [
        {
            "id": "stage1",
            "duration": 5,
            "scenes": [
                {
                    "id": "scene1",
                    "motion": {"event": "fade"},
                    "camera": {"shot": "wide"},
                    "audio": {"track": "music"},
                    "continuity": {"previous": None},
                }
            ],
        }
    ]
}


class FakeGenerator:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def generate(self, prompt, parameters=None):
        if self.error is not None:
            raise self.error
        return self.result


class FakeRenderer:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def render(self, plan, parameters=None):
        if self.error is not None:
            raise self.error
        return self.result


class VideoCommandParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    def test_video_prefix_english(self):
        task = self.parser.parse("video generate a sunset")
        self.assertEqual(task.task_type, "video")

    def test_video_prefix_arabic(self):
        task = self.parser.parse("فيديو generate a sunset")
        self.assertEqual(task.task_type, "video")

    def test_video_render_prefix(self):
        task = self.parser.parse("video render " + json.dumps(PLAN))
        self.assertEqual(task.task_type, "video")

    def test_video_preserves_command(self):
        task = self.parser.parse("video generate test")
        self.assertEqual(task.command, "video generate test")


class VideoCapabilityAgentTests(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    def test_generate_routes_to_execute(self):
        gen = FakeGenerator(
            result=Result.ok(data={"path": "/tmp/v.mp4"})
        )
        svc = VideoProductionService(generator=gen)
        services = {"video_production_service": svc}
        agent = CapabilityAgent(
            services, "video", "video_production_service", "execute"
        )
        task = self.parser.parse("video generate a cat")
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_render_routes_to_execute(self):
        rnd = FakeRenderer(
            result=Result.ok(data={"path": "/tmp/rendered.mp4"})
        )
        svc = VideoProductionService(renderer=rnd)
        services = {"video_production_service": svc}
        agent = CapabilityAgent(
            services, "video", "video_production_service", "execute"
        )
        task = self.parser.parse("video render " + json.dumps(PLAN))
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_no_provider_returns_failure(self):
        svc = VideoProductionService()
        services = {"video_production_service": svc}
        agent = CapabilityAgent(
            services, "video", "video_production_service", "execute"
        )
        task = self.parser.parse("video generate test")
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_missing_service(self):
        services = {}
        agent = CapabilityAgent(
            services, "video", "video_production_service", "execute"
        )
        task = self.parser.parse("video generate test")
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_unsupported_operation_in_body(self):
        svc = VideoProductionService()
        services = {"video_production_service": svc}
        agent = CapabilityAgent(
            services, "video", "video_production_service", "execute"
        )
        task = self.parser.parse("video download stuff")
        result = agent.execute(task)
        self.assertFalse(result.success)


class VideoServiceContainerTests(unittest.TestCase):
    def test_container_registers_video_service(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        svc = container.get("video_production_service")
        self.assertIsNotNone(svc)
        self.assertIsInstance(svc, VideoProductionService)

    def test_container_video_generate_no_provider(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        svc = container.get("video_production_service")
        result = svc.generate("test")
        self.assertFalse(result.success)

    def test_container_video_render_no_provider(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        svc = container.get("video_production_service")
        result = svc.render(PLAN)
        self.assertFalse(result.success)


class RouterVideoMappingTests(unittest.TestCase):
    def test_video_routes_to_execute(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        router = TaskRouter(container._services)
        agents = router.list_agents()
        self.assertIn("video", agents)


if __name__ == "__main__":
    unittest.main()
