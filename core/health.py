"""System health check for AllAffiliate_Agent.

Reports application state based on actual ServiceContainer and
MemoryManager initialization. Does not make external network calls.

States:
    HEALTHY     — all core components initialized
    DEGRADED    — non-critical component failed
    UNAVAILABLE — critical component failed
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from core.result import Result


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class HealthChecker:
    """Examines system state from existing service/provider state."""

    CRITICAL_SERVICES = {"memory_manager", "project_manager"}
    ALL_SERVICES = {
        "memory_manager",
        "project_manager",
        "cloud_ai_service",
        "research_service",
        "analysis_service",
        "workflow_service",
        "content_service",
        "digital_asset_service",
        "product_service",
        "policy_service",
        "video_production_service",
        "audio_service",
        "media_pipeline_service",
        "image_service",
        "browser_service",
        "computer_service",
        "publishing_service",
        "performance_monitoring_service",
        "diagnosis_service",
        "experiment_service",
        "command_dispatcher",
    }

    def __init__(self, service_container: Any) -> None:
        self._container = service_container

    def check(self) -> Result:
        """Run health checks and return a normalized Result.

        Result.data contains:
            {
                "status": "healthy" | "degraded" | "unavailable",
                "services": { "name": "ok" | "missing", ... },
                "initialized": bool,
                "total_services": int,
                "available_services": int,
            }
        """
        container_initialized = getattr(self._container, "is_initialized", True)

        services_report: dict[str, str] = {}
        missing_critical: list[str] = []
        missing_noncritical: list[str] = []

        for name in sorted(self.ALL_SERVICES):
            instance = self._container.get(name)
            if instance is not None:
                services_report[name] = "ok"
            else:
                services_report[name] = "missing"
                if name in self.CRITICAL_SERVICES:
                    missing_critical.append(name)
                else:
                    missing_noncritical.append(name)

        available = sum(1 for v in services_report.values() if v == "ok")
        total = len(self.ALL_SERVICES)

        if not container_initialized:
            status = HealthStatus.UNAVAILABLE
            message = "ServiceContainer is not initialized."
        elif missing_critical:
            status = HealthStatus.UNAVAILABLE
            message = f"Critical services missing: {', '.join(missing_critical)}"
        elif missing_noncritical:
            status = HealthStatus.DEGRADED
            message = f"Non-critical services missing: {', '.join(missing_noncritical)}"
        else:
            status = HealthStatus.HEALTHY
            message = "All services initialized."

        return Result.ok(
            message=message,
            data={
                "status": status.value,
                "services": services_report,
                "initialized": container_initialized,
                "total_services": total,
                "available_services": available,
            },
        )
