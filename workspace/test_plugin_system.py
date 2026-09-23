"""Tests for Plugin System (Batch 5)."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.plugin_contract import PluginContract
from core.plugin_loader import PluginLoader
from core.plugin_registry import PluginRegistry, PluginState


# ── Helpers ──────────────────────────────────────────────────────


def _write_plugin(directory: Path, filename: str, content: str) -> Path:
    p = directory / filename
    p.write_text(content, encoding="utf-8")
    return p


GOOD_PLUGIN = '''
class Plugin:
    @property
    def id(self):
        return "test_plugin"

    @property
    def name(self):
        return "Test Plugin"

    def initialize(self, services, router=None):
        pass

    def shutdown(self):
        pass
'''

GOOD_PLUGIN_2 = '''
class Plugin:
    @property
    def id(self):
        return "test_plugin_2"

    @property
    def name(self):
        return "Test Plugin 2"

    def initialize(self, services, router=None):
        pass

    def shutdown(self):
        pass
'''

SERVICE_REGISTERING_PLUGIN = '''
class Plugin:
    @property
    def id(self):
        return "service_plugin"

    @property
    def name(self):
        return "Service Plugin"

    def initialize(self, services, router=None):
        services.register("custom_service", {"type": "test"})

    def shutdown(self):
        pass
'''

AGENT_REGISTERING_PLUGIN = '''
from core.base_agent import BaseAgent
from core.result import Result

class _Agent(BaseAgent):
    task_type = "custom_task"
    name = "Custom Agent"

    def execute(self, task):
        return Result.ok(data="custom executed")

class Plugin:
    @property
    def id(self):
        return "agent_plugin"

    @property
    def name(self):
        return "Agent Plugin"

    def initialize(self, services, router=None):
        if router is not None:
            router.registry.register(_Agent())

    def shutdown(self):
        pass
'''

FAILING_INIT_PLUGIN = '''
class Plugin:
    @property
    def id(self):
        return "failing_init"

    @property
    def name(self):
        return "Failing Init"

    def initialize(self, services, router=None):
        raise RuntimeError("init boom")

    def shutdown(self):
        pass
'''

FAILING_SHUTDOWN_PLUGIN = '''
class Plugin:
    @property
    def id(self):
        return "failing_shutdown"

    @property
    def name(self):
        return "Failing Shutdown"

    def initialize(self, services, router=None):
        pass

    def shutdown(self):
        raise RuntimeError("shutdown boom")
'''

NO_ID_PLUGIN = '''
class Plugin:
    @property
    def id(self):
        return ""

    @property
    def name(self):
        return "No ID"

    def initialize(self, services, router=None):
        pass

    def shutdown(self):
        pass
'''

NO_PLUGIN_CLASS = '''
def not_a_plugin():
    pass
'''

BAD_SYNTAX = '''
class Plugin
    invalid python syntax
'''

SHUTDOWN_ORDER_PLUGIN_TEMPLATE = '''
_call_log = []

class Plugin:
    @property
    def id(self):
        return "{plugin_id}"

    @property
    def name(self):
        return "{plugin_id}"

    def initialize(self, services, router=None):
        _call_log.append(("init", "{plugin_id}"))

    def shutdown(self):
        _call_log.append(("shutdown", "{plugin_id}"))
'''


# ── PluginRegistry Tests ─────────────────────────────────────────


class TestPluginRegistry:
    def test_register_and_get(self):
        reg = PluginRegistry()
        plugin = MagicMock()
        plugin.id = "p1"
        assert reg.register(plugin) is True
        assert reg.get("p1") is plugin

    def test_duplicate_rejected(self):
        reg = PluginRegistry()
        p1 = MagicMock()
        p1.id = "dup"
        p2 = MagicMock()
        p2.id = "dup"
        assert reg.register(p1) is True
        assert reg.register(p2) is False

    def test_list_plugins(self):
        reg = PluginRegistry()
        p1 = MagicMock()
        p1.id = "a"
        p2 = MagicMock()
        p2.id = "b"
        reg.register(p1)
        reg.register(p2)
        assert reg.list_plugins() == ["a", "b"]

    def test_get_state(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = "s1"
        reg.register(p)
        assert reg.get_state("s1") == PluginState.REGISTERED

    def test_set_state(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = "s1"
        reg.register(p)
        reg.set_state("s1", PluginState.INITIALIZED)
        assert reg.get_state("s1") == PluginState.INITIALIZED

    def test_set_error(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = "e1"
        reg.register(p)
        reg.set_error("e1", "something broke")
        assert reg.get_state("e1") == PluginState.FAILED

    def test_is_loaded(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = "l1"
        assert reg.is_loaded("l1") is False
        reg.register(p)
        assert reg.is_loaded("l1") is True

    def test_remove(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = "r1"
        reg.register(p)
        assert reg.remove("r1") is True
        assert reg.get("r1") is None

    def test_initialized_plugins(self):
        reg = PluginRegistry()
        p1 = MagicMock()
        p1.id = "i1"
        p2 = MagicMock()
        p2.id = "i2"
        reg.register(p1)
        reg.register(p2)
        reg.set_state("i1", PluginState.INITIALIZED)
        assert reg.initialized_plugins() == ["i1"]

    def test_shutdown_all(self):
        reg = PluginRegistry()
        p1 = MagicMock()
        p1.id = "s1"
        p2 = MagicMock()
        p2.id = "s2"
        reg.register(p1)
        reg.register(p2)
        reg.set_state("s1", PluginState.INITIALIZED)
        reg.set_state("s2", PluginState.INITIALIZED)
        reg.shutdown_all()
        p2.shutdown.assert_called_once()
        p1.shutdown.assert_called_once()

    def test_shutdown_failure_isolated(self):
        reg = PluginRegistry()
        p1 = MagicMock()
        p1.id = "fail"
        p1.shutdown.side_effect = RuntimeError("boom")
        p2 = MagicMock()
        p2.id = "ok"
        reg.register(p1)
        reg.register(p2)
        reg.set_state("fail", PluginState.INITIALIZED)
        reg.set_state("ok", PluginState.INITIALIZED)
        reg.shutdown_all()
        p2.shutdown.assert_called_once()

    def test_shutdown_only_initialized(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = "disabled"
        reg.register(p)
        reg.set_state("disabled", PluginState.DISABLED)
        reg.shutdown_all()
        p.shutdown.assert_not_called()

    def test_missing_id_rejected(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = None
        assert reg.register(p) is False

    def test_empty_id_rejected(self):
        reg = PluginRegistry()
        p = MagicMock()
        p.id = "  "
        assert reg.register(p) is False


# ── PluginLoader Tests ──────────────────────────────────────────


class TestPluginLoaderDiscovery:
    def test_discover_valid_plugins(self, tmp_path):
        _write_plugin(tmp_path, "a.py", GOOD_PLUGIN)
        _write_plugin(tmp_path, "b.py", GOOD_PLUGIN_2)
        _write_plugin(tmp_path, "_private.py", GOOD_PLUGIN)
        _write_plugin(tmp_path, "readme.txt", "not a plugin")
        loader = PluginLoader(plugins_dir=tmp_path)
        found = loader.discover()
        assert found == ["a", "b"]

    def test_discover_empty_dir(self, tmp_path):
        loader = PluginLoader(plugins_dir=tmp_path)
        assert loader.discover() == []

    def test_discover_nonexistent_dir(self, tmp_path):
        loader = PluginLoader(plugins_dir=tmp_path / "nope")
        assert loader.discover() == []


class TestPluginLoaderLoading:
    def test_load_valid_plugin(self, tmp_path):
        _write_plugin(tmp_path, "good.py", GOOD_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        assert loader.registry.is_loaded("test_plugin")
        assert loader.registry.get_state("test_plugin") == PluginState.INITIALIZED

    def test_load_multiple_plugins(self, tmp_path):
        _write_plugin(tmp_path, "a.py", GOOD_PLUGIN)
        _write_plugin(tmp_path, "b.py", GOOD_PLUGIN_2)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        assert len(loader.registry.list_plugins()) == 2

    def test_deterministic_load_order(self, tmp_path):
        _write_plugin(tmp_path, "z_mod.py", GOOD_PLUGIN)
        _write_plugin(tmp_path, "a_mod.py", GOOD_PLUGIN_2)
        loader = PluginLoader(plugins_dir=tmp_path)
        discovered = loader.discover()
        assert discovered == ["a_mod", "z_mod"]

    def test_missing_plugin_class(self, tmp_path):
        _write_plugin(tmp_path, "noclass.py", NO_PLUGIN_CLASS)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        assert len(loader.registry.list_plugins()) == 0

    def test_invalid_syntax_isolated(self, tmp_path):
        _write_plugin(tmp_path, "bad.py", BAD_SYNTAX)
        _write_plugin(tmp_path, "good.py", GOOD_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        assert loader.registry.is_loaded("test_plugin")

    def test_failing_init_isolated(self, tmp_path):
        _write_plugin(tmp_path, "fail.py", FAILING_INIT_PLUGIN)
        _write_plugin(tmp_path, "good.py", GOOD_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        assert loader.registry.get_state("failing_init") == PluginState.FAILED
        assert loader.registry.get_state("test_plugin") == PluginState.INITIALIZED

    def test_empty_id_rejected(self, tmp_path):
        _write_plugin(tmp_path, "noid.py", NO_ID_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        assert len(loader.registry.list_plugins()) == 0

    def test_disabled_plugin_not_initialized(self, tmp_path):
        _write_plugin(tmp_path, "p1.py", GOOD_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock(), enabled=["other_plugin"])
        assert loader.registry.get_state("test_plugin") == PluginState.DISABLED


class TestPluginLoaderIntegration:
    def test_plugin_registers_service(self, tmp_path):
        _write_plugin(tmp_path, "svc.py", SERVICE_REGISTERING_PLUGIN)
        services = MagicMock()
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=services)
        services.register.assert_called_with("custom_service", {"type": "test"})

    def test_plugin_registers_agent(self, tmp_path):
        _write_plugin(tmp_path, "agent.py", AGENT_REGISTERING_PLUGIN)
        services = MagicMock()
        router = MagicMock()
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=services, router=router)
        router.registry.register.assert_called_once()

    def test_builtin_services_unaffected(self, tmp_path):
        services = MagicMock()
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=services)
        services.register.assert_not_called()


class TestPluginLoaderLifecycle:
    def test_shutdown_all_on_loader(self, tmp_path):
        _write_plugin(tmp_path, "p1.py", GOOD_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        loader.registry.shutdown_all()
        assert loader.registry.get_state("test_plugin") == PluginState.REGISTERED

    def test_shutdown_failure_isolated(self, tmp_path):
        _write_plugin(tmp_path, "fail.py", FAILING_SHUTDOWN_PLUGIN)
        _write_plugin(tmp_path, "good.py", GOOD_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        loader.registry.shutdown_all()
        assert loader.registry.get_state("test_plugin") == PluginState.REGISTERED

    def test_repeated_shutdown_safe(self, tmp_path):
        _write_plugin(tmp_path, "p1.py", GOOD_PLUGIN)
        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        loader.registry.shutdown_all()
        loader.registry.shutdown_all()

    def test_shutdown_order_reverse(self, tmp_path):
        import sys

        test_log = []
        sys.modules["_plugin_test_log"] = type(sys)("_plugin_test_log")
        sys.modules["_plugin_test_log"]._call_log = test_log

        p1_code = '''
import sys
_log = sys.modules["_plugin_test_log"]._call_log

class Plugin:
    @property
    def id(self):
        return "first"

    @property
    def name(self):
        return "first"

    def initialize(self, services, router=None):
        _log.append(("init", "first"))

    def shutdown(self):
        _log.append(("shutdown", "first"))
'''
        p2_code = '''
import sys
_log = sys.modules["_plugin_test_log"]._call_log

class Plugin:
    @property
    def id(self):
        return "second"

    @property
    def name(self):
        return "second"

    def initialize(self, services, router=None):
        _log.append(("init", "second"))

    def shutdown(self):
        _log.append(("shutdown", "second"))
'''
        _write_plugin(tmp_path, "first.py", p1_code)
        _write_plugin(tmp_path, "second.py", p2_code)

        loader = PluginLoader(plugins_dir=tmp_path)
        loader.load_all(services=MagicMock())
        loader.registry.shutdown_all()

        shutdowns = [pid for action, pid in test_log if action == "shutdown"]
        assert shutdowns == ["second", "first"]

        del sys.modules["_plugin_test_log"]
