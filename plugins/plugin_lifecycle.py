"""
plugins/plugin_lifecycle.py

Manages the operational state of registered plugins.

Lifecycle responsibilities are intentionally limited to:
    - enable
    - disable

Plugin loading, registration, removal, and discovery remain outside
this component.
"""

from __future__ import annotations

from typing import Any

from core.result import Result


class PluginLifecycle:
    """
    Manage enable/disable state for registered plugins.

    Initial state:
        Every registered plugin is considered disabled until explicitly
        enabled through this component.
    """

    def __init__(self, registry: Any) -> None:
        """
        Initialize the lifecycle manager.

        Args:
            registry:
                PluginRegistry-compatible object exposing:
                get(name: str) -> Result
        """
        self._registry = registry
        self._states: dict[str, str] = {}

    def enable(self, name: str) -> Result:
        """
        Enable a registered plugin.

        Returns:
            Result.ok(...) when the plugin changes from disabled to enabled.
            Result.fail(...) when the name is invalid, the plugin is not
            registered, or the plugin is already enabled.
        """
        plugin_name_result = self._validate_name(name)
        if not plugin_name_result.success:
            return plugin_name_result

        plugin_name = plugin_name_result.data

        registered = self._registry.get(plugin_name)
        if not registered.success:
            return Result.fail(
                message=f"الـPlugin غير مسجل: {plugin_name}",
                errors=registered.errors,
                metadata={"plugin": plugin_name},
            )

        current_state = self._states.get(plugin_name, "disabled")

        if current_state == "enabled":
            return Result.fail(
                message=f"الـPlugin مفعّل بالفعل: {plugin_name}",
                metadata={
                    "plugin": plugin_name,
                    "state": current_state,
                },
            )

        self._states[plugin_name] = "enabled"

        return Result.ok(
            data=registered.data,
            message=f"تم تفعيل الـPlugin: {plugin_name}",
            metadata={
                "plugin": plugin_name,
                "state": "enabled",
            },
        )

    def disable(self, name: str) -> Result:
        """
        Disable a registered plugin.

        Returns:
            Result.ok(...) when the plugin changes from enabled to disabled.
            Result.fail(...) when the name is invalid, the plugin is not
            registered, or the plugin is already disabled.
        """
        plugin_name_result = self._validate_name(name)
        if not plugin_name_result.success:
            return plugin_name_result

        plugin_name = plugin_name_result.data

        registered = self._registry.get(plugin_name)
        if not registered.success:
            return Result.fail(
                message=f"الـPlugin غير مسجل: {plugin_name}",
                errors=registered.errors,
                metadata={"plugin": plugin_name},
            )

        current_state = self._states.get(plugin_name, "disabled")

        if current_state == "disabled":
            return Result.fail(
                message=f"الـPlugin معطّل بالفعل: {plugin_name}",
                metadata={
                    "plugin": plugin_name,
                    "state": current_state,
                },
            )

        self._states[plugin_name] = "disabled"

        return Result.ok(
            data=registered.data,
            message=f"تم تعطيل الـPlugin: {plugin_name}",
            metadata={
                "plugin": plugin_name,
                "state": "disabled",
            },
        )

    def _validate_name(self, name: str) -> Result:
        """
        Validate and normalize a plugin name.
        """
        if not isinstance(name, str) or not name.strip():
            return Result.fail(
                message="اسم الـPlugin غير صالح.",
            )

        return Result.ok(
            data=name.strip(),
        )