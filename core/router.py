from core.logger import Logger
from core.registry import AgentRegistry
from core.result import Result

from agents.coding_agent import CodingAgent
from agents.memory_agent import MemoryAgent
from agents.browser_agent import BrowserAgent
from agents.computer_agent import ComputerAgent
from agents.capability_agent import CapabilityAgent


class TaskRouter:
    """
    Routes tasks to the appropriate Agent.

    TaskRouter is responsible only for agent registration
    and task routing.

    It does not contain business logic.
    """

    def __init__(self, services):

        self.services = services

        self.registry = AgentRegistry()

        # -----------------------------
        # Coding Agent
        # -----------------------------

        self.registry.register(
            CodingAgent(self.services)
        )

        # -----------------------------
        # Memory Agent
        # -----------------------------

        memory_manager = self.services.get("memory_manager")

        self.registry.register(
            MemoryAgent(memory_manager)
        )

        # -----------------------------
        # Browser Agent
        # -----------------------------

        self.registry.register(
            BrowserAgent(self.services)
        )

        # -----------------------------
        # Computer Agent
        # -----------------------------

        self.registry.register(
            ComputerAgent(self.services)
        )

        # -----------------------------
        # Service-only capability agents
        # -----------------------------

        capability_mappings = (
            ("research", "research_service", "research"),
            ("analyze", "analysis_service", "analyze"),
            ("plan", "workflow_service", "plan"),
            ("content", "content_service", "create"),
            ("video", "video_production_service", "execute"),
            ("audio", "audio_service", "execute"),
            ("media", "media_pipeline_service", "compose"),
            ("asset", "digital_asset_service", "register"),
            ("product", "product_service", "rank"),
            ("policy", "policy_service", "evaluate"),
            ("monitor", "performance_monitoring_service", "record"),
            ("diagnose", "diagnosis_service", "diagnose"),
            ("experiment", "experiment_service", "create"),
            ("publishing", "publishing_service", "publish"),
            ("image", "image_service", "execute"),
        )
        for task_type, service_name, method_name in capability_mappings:
            self.registry.register(
                CapabilityAgent(
                    self.services,
                    task_type,
                    service_name,
                    method_name,
                )
            )

    # --------------------------------------------------
    # Routing
    # --------------------------------------------------

    def route(self, task) -> Result:
        """
        Route a task to the registered Agent
        responsible for its task type.
        """

        agent = self.registry.get(task.task_type)

        if agent is None:

            Logger.warning(
                "لا يوجد Agent لهذه المهمة."
            )

            return Result.fail(
                message="لا يوجد وكيل مناسب."
            )

        return agent.execute(task)

    # --------------------------------------------------
    # Agent Registry
    # --------------------------------------------------

    def list_agents(self) -> list[str]:
        """
        Return the registered agent task types.
        """

        return self.registry.list_agents()
