"""Plugin registry for AllAffiliate_Agent.

Manages plugin instances, lifecycle states, and enable/disable state.
Does not discover or load plugins — that is PluginLoader's responsibility.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from core.logger import Logger


class PluginState(str, Enum):
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    DISABLED = "disabled"
    FAILED = "failed"


class PluginRecord:
    """Internal record for one loaded plugin."""

    __slots__ = ("plugin", "state", "error")

    def __init__(self, plugin: Any, state: PluginState) -> None:
        self.plugin = plugin
        self.state = state
        self.error: str | None = None


class PluginRegistry:
    """Central registry for loaded plugins.

    Prevents duplicate plugin IDs. Tracks lifecycle state.
    """

    def __init__(self) -> None:
        self._plugins: dict[str, PluginRecord] = {}

    def register(self, plugin: Any) -> bool:
        """Register a plugin instance.

        Returns True on success, False if duplicate or invalid.
        """
        plugin_id = getattr(plugin, "id", None)
        if not isinstance(plugin_id, str) or not plugin_id.strip():
            Logger.warning("Plugin rejected: missing or empty id.")
            return False

        plugin_id = plugin_id.strip()

        if plugin_id in self._plugins:
            Logger.warning(f"Plugin '{plugin_id}' rejected: duplicate id.")
            return False

        self._plugins[plugin_id] = PluginRecord(plugin, PluginState.REGISTERED)
        return True

    def get(self, plugin_id: str) -> Any | None:
        record = self._plugins.get(plugin_id)
        return record.plugin if record else None

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())

    def get_state(self, plugin_id: str) -> PluginState | None:
        record = self._plugins.get(plugin_id)
        return record.state if record else None

    def set_state(self, plugin_id: str, state: PluginState) -> None:
        record = self._plugins.get(plugin_id)
        if record:
            record.state = state

    def set_error(self, plugin_id: str, error: str) -> None:
        record = self._plugins.get(plugin_id)
        if record:
            record.error = error
            record.state = PluginState.FAILED

    def is_loaded(self, plugin_id: str) -> bool:
        return plugin_id in self._plugins

    def remove(self, plugin_id: str) -> bool:
        if plugin_id in self._plugins:
            del self._plugins[plugin_id]
            return True
        return False

    def initialized_plugins(self) -> list[str]:
        return [
            pid for pid, rec in self._plugins.items()
            if rec.state == PluginState.INITIALIZED
        ]

    def failed_plugins(self) -> list[str]:
        return [
            pid for pid, rec in self._plugins.items()
            if rec.state == PluginState.FAILED
        ]

    def shutdown_all(self) -> None:
        """Shutdown all initialized plugins in reverse registration order."""
        for plugin_id in reversed(list(self._plugins.keys())):
            record = self._plugins[plugin_id]
            if record.state != PluginState.INITIALIZED:
                continue
            try:
                record.plugin.shutdown()
            except Exception as exc:
                Logger.warning(f"Plugin '{plugin_id}' shutdown failed: {exc}")
            record.state = PluginState.REGISTERED
