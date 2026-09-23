"""Tests for HealthChecker and lifecycle (Batch 2)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.health import HealthChecker, HealthStatus
from core.result import Result
from core.service_container import ServiceContainer


# ── Health Check Tests ───────────────────────────────────────────


class TestHealthCheckerConstruction:
    def test_import(self):
        from core.health import HealthChecker
        assert HealthChecker is not None

    def test_status_enum(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNAVAILABLE.value == "unavailable"


class TestHealthCheckerHealthy:
    def test_all_services_present(self):
        container = ServiceContainer()
        checker = HealthChecker(container)
        result = checker.check()
        assert result.success is True
        assert result.data["status"] == "healthy"
        assert result.data["initialized"] is True
        assert result.data["available_services"] == result.data["total_services"]

    def test_returns_result_contract(self):
        container = ServiceContainer()
        checker = HealthChecker(container)
        result = checker.check()
        assert isinstance(result, Result)


class TestHealthCheckerDegraded:
    def test_missing_noncritical_service(self):
        container = MagicMock()
        container.get = MagicMock(side_effect=lambda name: None if name == "experiment_service" else MagicMock())
        checker = HealthChecker(container)
        result = checker.check()
        assert result.data["status"] == "degraded"
        assert "experiment_service" in result.message

    def test_multiple_missing_noncritical(self):
        container = MagicMock()
        missing = {"experiment_service", "diagnosis_service", "publishing_service"}
        container.get = MagicMock(side_effect=lambda name: None if name in missing else MagicMock())
        checker = HealthChecker(container)
        result = checker.check()
        assert result.data["status"] == "degraded"


class TestHealthCheckerUnavailable:
    def test_missing_memory_manager(self):
        container = MagicMock()
        container.get = MagicMock(return_value=None)
        checker = HealthChecker(container)
        result = checker.check()
        assert result.data["status"] == "unavailable"
        assert "memory_manager" in result.message

    def test_missing_project_manager(self):
        container = MagicMock()
        def fake_get(name):
            if name == "project_manager":
                return None
            if name == "memory_manager":
                return MagicMock()
            return MagicMock()
        container.get = MagicMock(side_effect=fake_get)
        checker = HealthChecker(container)
        result = checker.check()
        assert result.data["status"] == "unavailable"
        assert "project_manager" in result.message


class TestHealthCheckerNoNetwork:
    def test_no_external_calls(self):
        container = ServiceContainer()
        checker = HealthChecker(container)
        result = checker.check()
        assert result.success is True
        services = result.data["services"]
        assert all(v == "ok" for v in services.values())


# ── ServiceContainer Lifecycle Tests ─────────────────────────────


class TestServiceContainerLifecycle:
    def test_shutdown_idempotent(self):
        container = ServiceContainer()
        container.shutdown()
        container.shutdown()

    def test_shutdown_sets_initialized_false(self):
        container = ServiceContainer()
        assert container.is_initialized is True
        container.shutdown()
        assert container.is_initialized is False

    def test_shutdown_calls_close_on_services(self):
        container = ServiceContainer()
        mock_service = MagicMock()
        container.register("test_service", mock_service)
        container.shutdown()
        mock_service.close.assert_called_once()

    def test_shutdown_handles_close_failure(self):
        container = ServiceContainer()
        mock_service = MagicMock()
        mock_service.close.side_effect = RuntimeError("boom")
        container.register("fail_service", mock_service)
        container.shutdown()

    def test_shutdown_releases_in_reverse_order(self):
        container = ServiceContainer()
        call_order = []
        for i in range(3):
            mock = MagicMock()
            mock.close.side_effect = lambda idx=i: call_order.append(idx)
            container.register(f"svc_{i}", mock)
        container.shutdown()
        assert call_order == [2, 1, 0]


# ── MemoryManager Lifecycle Tests ────────────────────────────────


class TestMemoryManagerLifecycle:
    def test_close_is_idempotent(self):
        from memory.memory_manager import MemoryManager
        mm = MemoryManager(":memory:")
        mm.close()
        mm.close()

    def test_close_allows_health_check(self):
        from memory.memory_manager import MemoryManager
        mm = MemoryManager(":memory:")
        mm.close()
        assert mm.health_check() is True


# ── MasterAgent Lifecycle Tests ──────────────────────────────────


class TestMasterAgentLifecycle:
    def test_shutdown_idempotent(self):
        from agents.master_agent import MasterAgent
        agent = MasterAgent()
        agent.shutdown()
        agent.shutdown()

    def test_shutdown_clears_shutdown_flag(self):
        from agents.master_agent import MasterAgent
        agent = MasterAgent()
        assert agent._shutdown_done is False
        agent.shutdown()
        assert agent._shutdown_done is True

    def test_health_check_returns_result(self):
        from agents.master_agent import MasterAgent
        agent = MasterAgent()
        result = agent.health_check()
        assert isinstance(result, Result)
        assert result.success is True
        assert "status" in result.data
        agent.shutdown()

    def test_health_check_after_shutdown(self):
        from agents.master_agent import MasterAgent
        agent = MasterAgent()
        agent.shutdown()
        result = agent.health_check()
        assert result.data["status"] == "unavailable"

    def test_execute_after_shutdown_starts_new_session(self):
        from agents.master_agent import MasterAgent
        agent = MasterAgent()
        agent.shutdown()
        assert agent.session_id == ""

    def test_end_session_twice_returns_fail(self):
        from agents.master_agent import MasterAgent
        agent = MasterAgent()
        r1 = agent.end_session()
        assert r1.success is True
        r2 = agent.end_session()
        assert r2.success is False
