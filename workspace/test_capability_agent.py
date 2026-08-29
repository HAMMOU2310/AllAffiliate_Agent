import unittest
from types import SimpleNamespace

from agents.capability_agent import CapabilityAgent
from core.command_parser import CommandParser
from core.result import Result
from core.router import TaskRouter
from core.service_container import ServiceContainer


class FakeResearchService:
    def __init__(self):
        self.queries = []

    def research(self, query, scope=None):
        self.queries.append((query, scope))
        return Result.ok(data=[{"kind": "FACT", "content": query}])


class FakeServices:
    def __init__(self, service=None):
        self.service = service

    def get(self, name):
        return self.service if name == "research_service" else None


class CapabilityAgentTests(unittest.TestCase):
    def test_structured_payload_propagates_service_result(self):
        service = FakeResearchService()
        agent = CapabilityAgent(
            FakeServices(service), "research", "research_service", "research"
        )
        result = agent.execute(
            SimpleNamespace(data={"payload": {"query": "plants", "scope": "local"}})
        )
        self.assertTrue(result.success)
        self.assertEqual(service.queries, [("plants", "local")])

    def test_string_capability_uses_command_body(self):
        service = FakeResearchService()
        agent = CapabilityAgent(
            FakeServices(service), "research", "research_service", "research"
        )
        result = agent.execute(SimpleNamespace(data={}, command="research plants"))
        self.assertTrue(result.success)
        self.assertEqual(service.queries, [("plants", None)])

    def test_invalid_payload_and_missing_service_fail_as_result(self):
        agent = CapabilityAgent(
            FakeServices(), "analyze", "analysis_service", "analyze"
        )
        missing = agent.execute(SimpleNamespace(data={"payload": {}}))
        self.assertFalse(missing.success)

        agent = CapabilityAgent(
            FakeServices(FakeResearchService()),
            "analyze",
            "analysis_service",
            "analyze",
        )
        invalid = agent.execute(SimpleNamespace(data={}, command="analyze"))
        self.assertFalse(invalid.success)

    def test_parser_and_router_expose_documented_capabilities(self):
        parser = CommandParser()
        self.assertEqual(parser.parse("research plants").task_type, "research")
        self.assertEqual(parser.parse("\u0627\u0628\u062d\u062b \u0627\u0644\u0646\u0628\u0627\u062a").task_type, "research")

        router = TaskRouter(ServiceContainer())
        expected = {
            "research", "analyze", "plan", "content", "video", "audio",
            "media", "asset", "product", "policy", "monitor", "diagnose",
            "experiment", "publishing",
        }
        self.assertTrue(expected.issubset(set(router.list_agents())))


if __name__ == "__main__":
    unittest.main()
