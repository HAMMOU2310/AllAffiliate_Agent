import unittest

from core.result import Result
from core.router import TaskRouter
from core.task import Task
from services.analysis_service import AnalysisService
from services.audio_service import AudioService
from services.content_service import ContentService
from services.diagnosis_service import DiagnosisService
from services.digital_asset_service import DigitalAssetService
from services.experiment_service import ExperimentService
from services.media_pipeline_service import MediaPipelineService
from services.performance_monitoring_service import PerformanceMonitoringService
from services.policy_service import PolicyService
from services.product_service import ProductService
from services.publishing_service import PublishingService
from services.research_service import ResearchService
from services.video_production_service import VideoProductionService
from services.workflow_service import WorkflowService


class Source:
    def search(self, query, scope=None):
        return Result.ok(data=[{
            "source": "local-fixture",
            "title": "Evidence",
            "content": query,
            "kind": "FACT",
        }])


class Planner:
    def plan(self, goal, context=None):
        return Result.ok(data=[{
            "id": "research",
            "description": goal,
            "status": "READY",
        }])


class ContentGenerator:
    def generate(self, brief, persona=None, format=None):
        return Result.ok(data={"title": "Draft", "body": brief, "claims": []})


class VideoInterpreter:
    def interpret(self, instruction):
        return Result.ok(data={"timeline": [{
            "id": "stage-1",
            "duration": 4,
            "scenes": [{
                "id": "scene-1",
                "motion": {"type": "growth"},
                "camera": {"type": "static"},
                "audio": {"tracks": []},
                "continuity": {"subject": "plant"},
            }],
        }]})


class AudioInterpreter:
    def interpret(self, instruction):
        return Result.ok(data={"tracks": [{
            "id": "narration",
            "kind": "narration",
            "start": 0,
            "duration": 4,
            "content": instruction,
            "continuity": {"subject": "plant"},
        }]})


class PolicyEvaluator:
    def __init__(self, decision):
        self.decision = decision

    def evaluate(self, asset):
        return Result.ok(data={"decision": self.decision, "reasons": ["fixture"]})


class Publisher:
    def publish(self, asset, destination):
        return Result.ok(data={"destination": destination})


class DiagnosisAnalyzer:
    def analyze(self, asset_id, observations):
        return Result.ok(data=[
            {"kind": "FACT", "content": "clicks declined"},
            {"kind": "HYPOTHESIS", "content": "the offer may need review"},
            {"kind": "RECOMMENDATION", "content": "run a controlled experiment"},
        ])


class Dispatcher:
    def __init__(self):
        self.commands = []

    def dispatch(self, command):
        self.commands.append(command)
        return Result.ok(data={"command": command})


class Container:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def get(self, name):
        if name == "command_dispatcher":
            return self.dispatcher
        return None


class V1IntegrationTests(unittest.TestCase):
    def test_router_agent_dispatcher_result_flow(self):
        dispatcher = Dispatcher()
        router = TaskRouter(Container(dispatcher))
        result = router.route(Task(task_type="coding", command="list"))
        self.assertTrue(result.success)
        self.assertEqual(dispatcher.commands, ["list"])

    def test_goal_planning_research_and_analysis_flow(self):
        plan = WorkflowService(Planner()).plan("research temporal video trends")
        self.assertTrue(plan.success)
        evidence = ResearchService([Source()]).research("temporal video trends")
        analyzed = AnalysisService().analyze(evidence.data, "what is known?")
        self.assertTrue(analyzed.success)
        self.assertEqual(analyzed.data[0]["kind"], "FACT")

    def test_content_video_audio_and_media_flow(self):
        draft = ContentService(ContentGenerator()).create("Explain plant growth", format="script")
        video = VideoProductionService(VideoInterpreter()).create_plan(draft.data["body"])
        audio = AudioService(AudioInterpreter()).create_plan("Narrate plant growth")
        composed = MediaPipelineService().compose(video.data, audio.data)
        self.assertTrue(composed.success)
        self.assertEqual(composed.metadata["stage"], "VALIDATED")

    def test_asset_monitoring_diagnosis_experiment_and_learning_flow(self):
        asset = DigitalAssetService().register("video", "Plant growth")
        monitor = PerformanceMonitoringService()
        monitor.record(asset.data["id"], {"views": 100, "clicks": 4})
        observations = monitor.list_observations(asset.data["id"])
        evidence = [{"content": str(observation["metrics"])} for observation in observations.data]
        diagnosis = DiagnosisService(DiagnosisAnalyzer()).diagnose(asset.data["id"], evidence)
        experiment_service = ExperimentService()
        experiment = experiment_service.create(
            asset.data["id"], diagnosis.data[1]["content"], "change CTA"
        )
        measurement = experiment_service.record_measurement(
            experiment.data["id"], {"clicks": 6}
        )
        completed = experiment_service.complete(
            experiment.data["id"], "clicks improved", "retain the CTA change"
        )
        self.assertEqual(measurement.data["asset_id"], asset.data["id"])
        self.assertTrue(diagnosis.success)
        self.assertTrue(completed.success)

    def test_product_policy_and_publishing_flow(self):
        ranked = ProductService().rank([{
            "id": "product-1",
            "name": "Useful product",
            "signals": {"fit": 0.9, "evidence": 0.8},
        }])
        asset = {"id": ranked.data[0]["id"], "name": ranked.data[0]["name"]}
        allowed = PolicyService(PolicyEvaluator("ALLOWED")).evaluate(asset)
        published = PublishingService(Publisher()).publish(
            {**asset, "policy": allowed.data}, "fixture-platform"
        )
        blocked = PolicyService(PolicyEvaluator("BLOCKED")).evaluate(asset)
        rejected = PublishingService(Publisher()).publish(
            {**asset, "policy": blocked.data}, "fixture-platform"
        )
        self.assertTrue(published.success)
        self.assertFalse(rejected.success)


if __name__ == "__main__":
    unittest.main()
