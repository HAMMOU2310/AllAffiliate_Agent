from dotenv import load_dotenv

from services.project_manager import ProjectManager
from services.cloud_ai_service import CloudAIService
from providers.openai_provider import OpenAIProvider
from providers.gemini_provider import GeminiProvider
from providers.cloud_ai_content_generator import CloudAIContentGenerator
from services.research_service import ResearchService
from providers.openserp_search_provider import OpenSERPSearchProvider
from services.analysis_service import AnalysisService
from services.workflow_service import WorkflowService
from services.content_service import ContentService
from services.digital_asset_service import DigitalAssetService
from services.product_service import ProductService
from services.policy_service import PolicyService
from services.video_production_service import VideoProductionService
from providers.gemini_video_provider import GeminiVideoProvider
from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
from services.audio_service import AudioService
from services.media_pipeline_service import MediaPipelineService
from services.image_service import ImageService
from providers.local_image_provider import LocalImageProvider
from providers.gemini_image_provider import GeminiImageProvider
from providers.gemini_voice_provider import GeminiSTTProvider, GeminiTTSProvider
from services.browser_service import BrowserService
from providers.search_browser_adapter import SearchBrowserAdapter
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

    Lifecycle:
        shutdown() releases resources held by services that implement
        a close() method.  Idempotent — safe to call multiple times.
    """

    def __init__(self):
        load_dotenv()

        self._services = {}

        self._initialized = False

        self._initialize_services()

        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def _initialize_services(self):
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

        cloud_ai = CloudAIService()
        cloud_ai.register_provider("openai", OpenAIProvider())
        cloud_ai.register_provider("gemini", GeminiProvider())
        self.register("cloud_ai_service", cloud_ai)

        # -----------------------------
        # Intelligence and planning services
        # -----------------------------

        self.register("research_service", ResearchService([OpenSERPSearchProvider()]))
        self.register("analysis_service", AnalysisService())
        self.register("workflow_service", WorkflowService())

        content_generator = CloudAIContentGenerator(
            cloud_ai_service=cloud_ai,
            model="gpt-4o-mini",
        )
        self.register("content_service", ContentService(content_generator))
        self.register("digital_asset_service", DigitalAssetService())
        self.register("product_service", ProductService())
        self.register("policy_service", PolicyService())

        # -----------------------------
        # Production and computer-operation services
        # -----------------------------

        self.register(
            "video_production_service",
            VideoProductionService(
                generator=GeminiVideoProvider(),
                renderer=FFmpegVideoRenderer(),
            ),
        )
        self.register(
            "audio_service",
            AudioService(
                stt_provider=GeminiSTTProvider(),
                tts_provider=GeminiTTSProvider(),
            ),
        )
        self.register("media_pipeline_service", MediaPipelineService())
        search_provider = OpenSERPSearchProvider()
        self.register(
            "browser_service",
            BrowserService(SearchBrowserAdapter(search_provider)),
        )
        self.register(
            "computer_service",
            ComputerService(permitted=False),
        )
        self.register(
            "image_service",
            ImageService(
                generator=GeminiImageProvider(),
                processor=LocalImageProvider(),
            ),
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

    def shutdown(self) -> None:
        """Release resources held by services.

        Iterates registered services in reverse registration order.
        Calls close() on services that implement it.
        Failures are logged but never propagated.
        Idempotent — safe to call repeatedly.
        """
        if not self._initialized:
            return

        from core.logger import Logger

        for name in reversed(list(self._services.keys())):
            service = self._services.get(name)
            if service is None:
                continue
            closer = getattr(service, "close", None)
            if callable(closer):
                try:
                    closer()
                except Exception as exc:
                    Logger.warning(
                        f"Cleanup failed for {name}: {exc}"
                    )

        self._initialized = False
