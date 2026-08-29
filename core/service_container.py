from dotenv import load_dotenv

from services.code_writer import CodeWriter
from services.python_runner import PythonRunner
from services.file_tools import FileTools
from services.text_editor import TextEditor
from services.project_manager import ProjectManager
from services.cloud_ai_service import CloudAIService
from services.research_service import ResearchService
from services.analysis_service import AnalysisService
from services.workflow_service import WorkflowService
from services.content_service import ContentService
from services.digital_asset_service import DigitalAssetService
from services.product_service import ProductService
from services.policy_service import PolicyService
from services.persona_service import PersonaService
from services.affiliate_identity_service import AffiliateIdentityService
from services.video_production_service import VideoProductionService
from services.audio_service import AudioService
from services.media_pipeline_service import MediaPipelineService
from services.browser_service import BrowserService
from services.computer_service import ComputerService
from services.publishing_service import PublishingService
from services.performance_monitoring_service import PerformanceMonitoringService
from services.diagnosis_service import DiagnosisService
from services.experiment_service import ExperimentService

from memory.memory_manager import MemoryManager

from core.command_dispatcher import CommandDispatcher


class ServiceContainer:
    """
    Central container for project services.

    Responsible for creating and registering
    shared service instances used by the application.
    """

    def __init__(self):
        load_dotenv()

        self._services = {}

        self._initialize_services()

    def _initialize_services(self):
        # -----------------------------
        # Code Writer
        # -----------------------------

        self.register(
            "code_writer",
            CodeWriter(),
        )

        # -----------------------------
        # Python Runner
        # -----------------------------

        self.register(
            "python_runner",
            PythonRunner(),
        )

        # -----------------------------
        # File Tools
        # -----------------------------

        self.register(
            "file_tools",
            FileTools(),
        )

        # -----------------------------
        # Text Editor
        # -----------------------------

        self.register(
            "text_editor",
            TextEditor(),
        )

        # -----------------------------
        # Project Manager
        # -----------------------------

        self.register(
            "project_manager",
            ProjectManager(),
        )

        # -----------------------------
        # Cloud AI Service
        # -----------------------------

        self.register(
            "cloud_ai_service",
            CloudAIService(),
        )

        # -----------------------------
        # Intelligence and planning services
        # -----------------------------

        self.register("research_service", ResearchService())
        self.register("analysis_service", AnalysisService())
        self.register("workflow_service", WorkflowService())
        self.register("content_service", ContentService())
        self.register("digital_asset_service", DigitalAssetService())
        self.register("product_service", ProductService())
        self.register("policy_service", PolicyService())
        self.register("persona_service", PersonaService())
        self.register("affiliate_identity_service", AffiliateIdentityService())

        # -----------------------------
        # Production and computer-operation services
        # -----------------------------

        self.register("video_production_service", VideoProductionService())
        self.register("audio_service", AudioService())
        self.register("media_pipeline_service", MediaPipelineService())
        self.register("browser_service", BrowserService())
        self.register(
            "computer_service",
            ComputerService(permitted=False),
        )
        self.register("publishing_service", PublishingService())
        self.register(
            "performance_monitoring_service",
            PerformanceMonitoringService(),
        )
        self.register("diagnosis_service", DiagnosisService())
        self.register("experiment_service", ExperimentService())

        # -----------------------------
        # Memory Manager
        # -----------------------------

        self.register(
            "memory_manager",
            MemoryManager(),
        )

        # -----------------------------
        # Command Dispatcher
        # -----------------------------

        self.register(
            "command_dispatcher",
            CommandDispatcher(self),
        )

    def register(self, service_name: str, service_instance):
        self._services[service_name] = service_instance

    def get(self, service_name: str):
        return self._services.get(service_name)
