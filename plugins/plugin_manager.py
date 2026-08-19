"""
plugins/plugin_manager.py

Manages loaded Python plugins through PluginLoader and PluginRegistry.

Responsibilities:
- Load plugins through PluginLoader.
- Register loaded plugins through PluginRegistry.
- Retrieve, remove, and list registered plugins.

This component does not:
- Perform dynamic discovery.
- Enable or disable plugins.
- Implement advanced plugin lifecycle.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Union

from core.result import Result
from plugins.plugin_loader import PluginLoader
from plugins.plugin_registry import PluginRegistry


PathLike = Union[str, Path]


class PluginManager:
    """Manage explicitly loaded plugins through Loader and Registry."""

    def __init__(
        self,
        loader: PluginLoader | None = None,
        registry: PluginRegistry | None = None,
    ) -> None:
        """Initialize PluginManager with optional Loader and Registry."""
        self._loader = loader or PluginLoader()
        self._registry = registry or PluginRegistry()

    def load(self, source: PathLike) -> Result:
        """
        Load one plugin through PluginLoader and register it.

        Returns:
            Result with the loaded module in data on success.
        """
        result = self._loader.load(source)

        if not result.success:
            return result

        module = result.data

        if not isinstance(module, ModuleType):
            return Result.fail(
                message="فشل تسجيل الـPlugin المحمّل.",
                errors=[
                    f"Unexpected plugin type: {type(module).__name__}",
                ],
            )

        module_name = str(
            result.metadata.get(
                "module_name",
                module.__name__,
            )
        )

        register_result = self._registry.register(
            module_name,
            module,
        )

        if not register_result.success:
            return register_result

        return Result.ok(
            data=module,
            message=f"تم تحميل وتسجيل الـPlugin بنجاح: {module_name}",
            metadata={
                "plugin": module_name,
                "count": register_result.metadata.get(
                    "count",
                    0,
                ),
            },
        )

    def get(self, name: str) -> Result:
        """Return a registered plugin by name."""
        return self._registry.get(name)

    def remove(self, name: str) -> Result:
        """Remove a registered plugin by name."""
        return self._registry.remove(name)

    def list(self) -> Result:
        """Return the names of all registered plugins."""
        return self._registry.list()

    @property
    def registry(self) -> PluginRegistry:
        """Return the PluginRegistry used by this manager."""
        return self._registry

    @property
    def loader(self) -> PluginLoader:
        """Return the PluginLoader used by this manager."""
        return self._loader