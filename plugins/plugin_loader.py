"""
plugins/plugin_loader.py

Responsible for loading a single Python plugin module.

The PluginLoader only handles module loading and returns the unified
Result contract. Plugin registration, management, discovery, and
lifecycle control belong to later components of v0.6.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from core.result import Result


class PluginLoader:
    """
    Loads a single Python plugin module from a file path.

    Responsibilities:
        - Validate the plugin path.
        - Validate that the target is a Python file.
        - Dynamically load the module.
        - Return Result.ok(...) on success.
        - Return Result.fail(...) on failure.

    This class does not:
        - Register plugins.
        - Manage plugin lifecycle.
        - Enable or disable plugins.
        - Discover multiple plugins.
        - Maintain a plugin registry.
    """

    def load(self, path: str | Path) -> Result:
        """
        Load a single Python plugin module.

        Args:
            path:
                Path to the Python plugin file.

        Returns:
            Result:
                Result.ok(data=module) on successful loading.
                Result.fail(...) on validation or loading failure.
        """
        try:
            plugin_path = Path(path)
        except (TypeError, ValueError) as exc:
            return Result.fail(
                message="مسار الـPlugin غير صالح.",
                errors=[str(exc)],
            )

        try:
            if not plugin_path.exists():
                return Result.fail(
                    message="ملف الـPlugin غير موجود.",
                    errors=[f"Plugin path does not exist: {plugin_path}"],
                )

            if not plugin_path.is_file():
                return Result.fail(
                    message="مسار الـPlugin لا يشير إلى ملف.",
                    errors=[f"Plugin path is not a file: {plugin_path}"],
                )

            if plugin_path.suffix.lower() != ".py":
                return Result.fail(
                    message="ملف الـPlugin يجب أن يكون ملف Python.",
                    errors=[
                        f"Unsupported plugin extension: {plugin_path.suffix}"
                    ],
                )

            resolved_path = plugin_path.resolve()

            module_name = resolved_path.stem
            if not module_name.isidentifier():
                return Result.fail(
                    message="اسم ملف الـPlugin غير صالح كاسم Module Python.",
                    errors=[
                        f"Invalid module name derived from plugin path: "
                        f"{module_name}"
                    ],
                )

            spec = importlib.util.spec_from_file_location(
                module_name,
                resolved_path,
            )

            if spec is None or spec.loader is None:
                return Result.fail(
                    message="تعذر إنشاء Loader للـPlugin.",
                    errors=[
                        f"Could not create import specification for: "
                        f"{resolved_path}"
                    ],
                )

            module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(module)

            if not isinstance(module, ModuleType):
                return Result.fail(
                    message="لم يتم تحميل الـPlugin كـPython Module صالح.",
                    errors=[
                        f"Unexpected loaded object type: {type(module).__name__}"
                    ],
                )

            return Result.ok(
                data=module,
                message="تم تحميل الـPlugin بنجاح.",
                metadata={
                    "plugin_path": str(resolved_path),
                    "module_name": module_name,
                },
            )

        except Exception as exc:
            return Result.fail(
                message="فشل تحميل الـPlugin.",
                errors=[f"{type(exc).__name__}: {exc}"],
                metadata={
                    "plugin_path": str(plugin_path),
                },
            )