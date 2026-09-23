import unittest

from core.result import Result
from core.task import Task
from core.command_parser import CommandParser
from core.router import TaskRouter
from agents.capability_agent import CapabilityAgent
from services.audio_service import AudioService


class FakeSTTProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.last_source = None
        self.last_params = None

    def transcribe(self, source, parameters=None):
        self.last_source = source
        self.last_params = parameters
        if self.error is not None:
            raise self.error
        return self.result


class FakeTTSProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.last_text = None
        self.last_params = None

    def synthesize(self, text, parameters=None):
        self.last_text = text
        self.last_params = parameters
        if self.error is not None:
            raise self.error
        return self.result


class AudioCommandParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    def test_audio_prefix_english(self):
        task = self.parser.parse("audio transcribe file.wav")
        self.assertEqual(task.task_type, "audio")

    def test_audio_prefix_arabic(self):
        task = self.parser.parse("صوت transcribe file.wav")
        self.assertEqual(task.task_type, "audio")

    def test_audio_speak_prefix(self):
        task = self.parser.parse("audio speak hello")
        self.assertEqual(task.task_type, "audio")

    def test_audio_create_plan_prefix(self):
        task = self.parser.parse("audio create_plan voice narration")
        self.assertEqual(task.task_type, "audio")

    def test_audio_preserves_command(self):
        task = self.parser.parse("audio transcribe test.wav")
        self.assertEqual(task.command, "audio transcribe test.wav")


class AudioCapabilityAgentTests(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    def test_transcribe_routes_to_execute(self):
        stt = FakeSTTProvider(
            result=Result.ok(data={"text": "hello"})
        )
        svc = AudioService(stt_provider=stt)
        services = {"audio_service": svc}
        agent = CapabilityAgent(
            services, "audio", "audio_service", "execute"
        )
        task = self.parser.parse("audio transcribe file.wav")
        result = agent.execute(task)
        self.assertTrue(result.success)
        self.assertEqual(result.data["text"], "hello")

    def test_speak_routes_to_execute(self):
        tts = FakeTTSProvider(
            result=Result.ok(data={"path": "/tmp/out.wav"})
        )
        svc = AudioService(tts_provider=tts)
        services = {"audio_service": svc}
        agent = CapabilityAgent(
            services, "audio", "audio_service", "execute"
        )
        task = self.parser.parse("audio speak hello world")
        result = agent.execute(task)
        self.assertTrue(result.success)

    def test_no_provider_returns_failure(self):
        svc = AudioService()
        services = {"audio_service": svc}
        agent = CapabilityAgent(
            services, "audio", "audio_service", "execute"
        )
        task = self.parser.parse("audio transcribe file.wav")
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_missing_service(self):
        services = {}
        agent = CapabilityAgent(
            services, "audio", "audio_service", "execute"
        )
        task = self.parser.parse("audio transcribe file.wav")
        result = agent.execute(task)
        self.assertFalse(result.success)

    def test_unsupported_operation_in_body(self):
        svc = AudioService()
        services = {"audio_service": svc}
        agent = CapabilityAgent(
            services, "audio", "audio_service", "execute"
        )
        task = self.parser.parse("audio volume up")
        result = agent.execute(task)
        self.assertFalse(result.success)


class AudioServiceContainerTests(unittest.TestCase):
    def test_container_registers_audio_service(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        svc = container.get("audio_service")
        self.assertIsNotNone(svc)
        self.assertIsInstance(svc, AudioService)

    def test_container_audio_transcribe_no_provider(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        svc = container.get("audio_service")
        result = svc.transcribe("test.wav")
        self.assertFalse(result.success)

    def test_container_audio_speak_no_provider(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        svc = container.get("audio_service")
        result = svc.speak("hello")
        self.assertFalse(result.success)


class RouterAudioMappingTests(unittest.TestCase):
    def test_audio_routes_to_execute(self):
        from core.service_container import ServiceContainer
        container = ServiceContainer()
        router = TaskRouter(container._services)
        agents = router.list_agents()
        self.assertIn("audio", agents)


if __name__ == "__main__":
    unittest.main()
