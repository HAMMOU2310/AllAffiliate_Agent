"""Plugin loader for AllAffiliate_Agent.

Discovers and loads plugin modules from the configured plugins directory.
Each plugin module must define a top-level `Plugin` class.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any

from core.logger import Logger
from core.plugin_registry import PluginRegistry, PluginState


class PluginLoader:
    """Discover, load, and initialize plugins from a directory."""

    def __init__(
        self,
        plugins_dir: str | Path = "plugins",
        registry: PluginRegistry | None = None,
    ) -> None:
        self._plugins_dir = Path(plugins_dir)
        self._registry = registry or PluginRegistry()

    @property
    def registry(self) -> PluginRegistry:
        return self._registry

    def discover(self) -> list[str]:
        """Return sorted list of .py plugin filenames in plugins_dir."""
        if not self._plugins_dir.is_dir():
            return []

        modules = []
        for entry in sorted(self._plugins_dir.iterdir()):
            if (
                entry.is_file()
                and entry.suffix == ".py"
                and not entry.name.startswith("_")
            ):
                modules.append(entry.stem)
        return modules

    def load_all(
        self,
        services: Any = None,
        router: Any = None,
        enabled: list[str] | None = None,
    ) -> PluginRegistry:
        """Discover, load, and initialize all plugins.

        Args:
            services: ServiceContainer for plugin registration.
            router: TaskRouter for agent registration (optional).
            enabled: If provided, only load plugins whose id is in this list.

        Returns:
            The PluginRegistry with loaded plugins.
        """
        module_names = self.discover()

        for module_name in module_names:
            self._load_module(module_name, services, router, enabled)

        return self._registry

    def _load_module(
        self,
        module_name: str,
        services: Any,
        router: Any,
        enabled: list[str] | None,
    ) -> None:
        module_path = self._plugins_dir / f"{module_name}.py"

        try:
            spec = importlib.util.spec_from_file_location(
                f"plugins.{module_name}",
                str(module_path),
            )
            if spec is None or spec.loader is None:
                Logger.warning(f"Plugin '{module_name}': cannot create module spec.")
                return

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        except Exception as exc:
            Logger.warning(f"Plugin '{module_name}': import failed: {exc}")
            return

        plugin_class = getattr(module, "Plugin", None)
        if plugin_class is None:
            Logger.warning(f"Plugin '{module_name}': no Plugin class found.")
            return

        try:
            plugin = plugin_class()
        except Exception as exc:
            Logger.warning(f"Plugin '{module_name}': instantiation failed: {exc}")
            return

        plugin_id = getattr(plugin, "id", None)
        if not isinstance(plugin_id, str) or not plugin_id.strip():
            Logger.warning(f"Plugin '{module_name}': missing or empty id.")
            return

        if not self._registry.register(plugin):
            return

        if enabled is not None and plugin_id not in enabled:
            self._registry.set_state(plugin_id, PluginState.DISABLED)
            Logger.info(f"Plugin '{plugin_id}' disabled by configuration.")
            return

        try:
            plugin.initialize(services, router)
            self._registry.set_state(plugin_id, PluginState.INITIALIZED)
            Logger.info(f"Plugin '{plugin_id}' initialized.")
        except Exception as exc:
            self._registry.set_error(plugin_id, str(exc))
            Logger.warning(f"Plugin '{plugin_id}' initialization failed: {exc}")
