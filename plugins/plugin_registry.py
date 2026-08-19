"""
plugins/plugin_registry.py

Central registry for explicitly registered Plugins.

Responsibilities:
- Register Plugins by name.
- Retrieve registered Plugins.
- Remove registered Plugins.
- List registered Plugin names.

This component does not:
- Load Python modules.
- Perform dynamic discovery.
- Enable or disable Plugins.
- Manage advanced Plugin lifecycle.
- Execute Core or Service logic.
"""

from __future__ import annotations

from typing import Any

from core.result import Result


class PluginRegistry:
    """Manage the central registry of registered Plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Any] = {}

    def register(self, name: str, plugin: object) -> Result:
        """
        Register a Plugin under a unique name.
        """
        if not isinstance(name, str) or not name.strip():
            return Result.fail(
                message="اسم الـPlugin غير صالح.",
            )

        if plugin is None:
            return Result.fail(
                message="كائن الـPlugin غير صالح.",
            )

        plugin_name = name.strip()

        if plugin_name in self._plugins:
            return Result.fail(
                message=f"الـPlugin مسجل مسبقًا: {plugin_name}",
                metadata={
                    "plugin": plugin_name,
                    "count": len(self._plugins),
                },
            )

        self._plugins[plugin_name] = plugin

        return Result.ok(
            data=plugin,
            message=f"تم تسجيل الـPlugin بنجاح: {plugin_name}",
            metadata={
                "plugin": plugin_name,
                "count": len(self._plugins),
            },
        )

    def get(self, name: str) -> Result:
        """
        Retrieve a registered Plugin by name.
        """
        if not isinstance(name, str) or not name.strip():
            return Result.fail(
                message="اسم الـPlugin غير صالح.",
            )

        plugin_name = name.strip()
        plugin = self._plugins.get(plugin_name)

        if plugin is None:
            return Result.fail(
                message=f"الـPlugin غير مسجل: {plugin_name}",
                metadata={
                    "plugin": plugin_name,
                },
            )

        return Result.ok(
            data=plugin,
            message=f"تم العثور على الـPlugin: {plugin_name}",
            metadata={
                "plugin": plugin_name,
            },
        )

    def remove(self, name: str) -> Result:
        """
        Remove a registered Plugin by name.
        """
        if not isinstance(name, str) or not name.strip():
            return Result.fail(
                message="اسم الـPlugin غير صالح.",
            )

        plugin_name = name.strip()

        if plugin_name not in self._plugins:
            return Result.fail(
                message=f"الـPlugin غير مسجل: {plugin_name}",
                metadata={
                    "plugin": plugin_name,
                },
            )

        plugin = self._plugins.pop(plugin_name)

        return Result.ok(
            data=plugin,
            message=f"تمت إزالة الـPlugin: {plugin_name}",
            metadata={
                "plugin": plugin_name,
                "count": len(self._plugins),
            },
        )

    def list(self) -> Result:
        """
        Return the names of all registered Plugins.
        """
        names = sorted(self._plugins)

        return Result.ok(
            data=names,
            message="تم جلب قائمة الـPlugins المسجلة.",
            metadata={
                "count": len(names),
            },
        )