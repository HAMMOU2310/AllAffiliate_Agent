"""
plugins/plugin_discovery.py

Discovers Python plugins from a directory and delegates their loading
to PluginManager.

Responsibilities:
    - Scan a directory for Python plugin files.
    - Ignore non-Python files.
    - Ignore __init__.py and private module files.
    - Delegate actual loading/registration to PluginManager.
    - Return a unified Result.

It does not:
    - Execute plugin capabilities.
    - Manage plugin lifecycle.
    - Modify PluginRegistry directly.
    - Perform capability discovery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.result import Result


class PluginDiscovery:
    """
    Discovers plugins from a filesystem directory.
    """

    def __init__(self, plugin_manager: Any) -> None:
        """
        Initialize discovery with a PluginManager-compatible object.
        """
        self._plugin_manager = plugin_manager

    def discover(self, path: str | Path) -> Result:
        """
        Discover Python plugins in the given directory.

        Args:
            path:
                Directory containing plugin Python files.

        Returns:
            Result.ok(...) with discovered plugin names when successful.
            Result.fail(...) when the directory is invalid or discovery
            cannot continue safely.
        """
        try:
            directory = Path(path)
        except (TypeError, ValueError) as exc:
            return Result.fail(
                message="مسار مجلد الـPlugins غير صالح.",
                errors=[str(exc)],
            )

        if not directory.exists():
            return Result.fail(
                message="مجلد الـPlugins غير موجود.",
                errors=[f"Directory does not exist: {directory}"],
            )

        if not directory.is_dir():
            return Result.fail(
                message="المسار المحدد ليس مجلدًا.",
                errors=[f"Path is not a directory: {directory}"],
            )

        discovered: list[str] = []
        failed: list[str] = []

        try:
            plugin_files = sorted(directory.glob("*.py"))
        except OSError as exc:
            return Result.fail(
                message="تعذر قراءة مجلد الـPlugins.",
                errors=[f"{type(exc).__name__}: {exc}"],
            )

        for plugin_file in plugin_files:
            module_name = plugin_file.stem

            if module_name == "__init__":
                continue

            if module_name.startswith("_"):
                continue

            result = self._plugin_manager.load(plugin_file)

            if result.success:
                discovered.append(module_name)
            else:
                failed.append(module_name)

        if failed:
            return Result.fail(
                message="فشل تحميل بعض الـPlugins المكتشفة.",
                errors=failed,
                metadata={
                    "discovered": discovered,
                    "failed": failed,
                    "count": len(discovered),
                },
            )

        return Result.ok(
            data=discovered,
            message="تم اكتشاف وتحميل الـPlugins بنجاح.",
            metadata={
                "discovered": discovered,
                "count": len(discovered),
                "path": str(directory.resolve()),
            },
        )