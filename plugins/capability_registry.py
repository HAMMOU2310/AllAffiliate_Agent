"""
plugins/capability_registry.py

Registers and discovers capabilities exposed by plugins.

This component is intentionally limited to capability registration,
lookup, listing, and removal.

It does not:
    - load plugins
    - register plugins
    - manage plugin lifecycle
    - execute capabilities
    - perform dynamic plugin discovery
"""

from __future__ import annotations

from typing import Any

from core.result import Result


class CapabilityRegistry:
    """
    Central registry for capabilities exposed by registered plugins.
    """

    def __init__(self) -> None:
        """
        Initialize an empty capability registry.

        Internal structure:

            {
                "plugin_name": {
                    "capability_name": capability_object
                }
            }
        """
        self._capabilities: dict[str, dict[str, Any]] = {}

    def register(
        self,
        plugin_name: str,
        capability_name: str,
        capability: object,
    ) -> Result:
        """
        Register a capability under a plugin.

        A capability with the same name cannot be registered twice
        under the same plugin.
        """
        plugin_result = self._validate_name(
            plugin_name,
            "اسم الـPlugin",
        )
        if not plugin_result.success:
            return plugin_result

        capability_result = self._validate_name(
            capability_name,
            "اسم الـCapability",
        )
        if not capability_result.success:
            return capability_result

        plugin = plugin_result.data
        name = capability_result.data

        if capability is None:
            return Result.fail(
                message="الـCapability غير صالحة.",
                metadata={
                    "plugin": plugin,
                    "capability": name,
                },
            )

        plugin_capabilities = self._capabilities.setdefault(plugin, {})

        if name in plugin_capabilities:
            return Result.fail(
                message=(
                    f"الـCapability مسجلة مسبقًا: "
                    f"{plugin}:{name}"
                ),
                metadata={
                    "plugin": plugin,
                    "capability": name,
                },
            )

        plugin_capabilities[name] = capability

        return Result.ok(
            data=capability,
            message=(
                f"تم تسجيل الـCapability بنجاح: "
                f"{plugin}:{name}"
            ),
            metadata={
                "plugin": plugin,
                "capability": name,
            },
        )

    def get(self, capability_name: str) -> Result:
        """
        Retrieve a capability by name.

        Capability names are globally unique from the public API
        perspective. When the same capability name exists under
        multiple plugins, the first matching registration in sorted
        plugin order is returned.
        """
        capability_result = self._validate_name(
            capability_name,
            "اسم الـCapability",
        )
        if not capability_result.success:
            return capability_result

        name = capability_result.data

        matches: list[tuple[str, Any]] = []

        for plugin in sorted(self._capabilities):
            capabilities = self._capabilities[plugin]

            if name in capabilities:
                matches.append(
                    (plugin, capabilities[name])
                )

        if not matches:
            return Result.fail(
                message=f"الـCapability غير مسجلة: {name}",
                metadata={
                    "capability": name,
                },
            )

        plugin, capability = matches[0]

        return Result.ok(
            data=capability,
            message=f"تم العثور على الـCapability: {name}",
            metadata={
                "plugin": plugin,
                "capability": name,
            },
        )

    def list(
        self,
        plugin_name: str | None = None,
    ) -> Result:
        """
        List registered capabilities.

        Without plugin_name:
            Returns all capabilities as fully qualified names:
            "plugin_name:capability_name"

        With plugin_name:
            Returns only the capability names belonging to that plugin.
        """
        if plugin_name is not None:
            plugin_result = self._validate_name(
                plugin_name,
                "اسم الـPlugin",
            )

            if not plugin_result.success:
                return plugin_result

            plugin = plugin_result.data

            if plugin not in self._capabilities:
                return Result.fail(
                    message=f"الـPlugin غير موجود: {plugin}",
                    metadata={
                        "plugin": plugin,
                    },
                )

            names = sorted(
                self._capabilities[plugin].keys()
            )

            return Result.ok(
                data=names,
                message="تم جلب Capabilities الخاصة بالـPlugin.",
                metadata={
                    "plugin": plugin,
                    "count": len(names),
                },
            )

        entries: list[str] = []

        for plugin in sorted(self._capabilities):
            for capability_name in sorted(
                self._capabilities[plugin]
            ):
                entries.append(
                    f"{plugin}:{capability_name}"
                )

        return Result.ok(
            data=entries,
            message="تم جلب جميع الـCapabilities.",
            metadata={
                "count": len(entries),
            },
        )

    def remove(
        self,
        plugin_name: str,
        capability_name: str,
    ) -> Result:
        """
        Remove a registered capability from a plugin.
        """
        plugin_result = self._validate_name(
            plugin_name,
            "اسم الـPlugin",
        )
        if not plugin_result.success:
            return plugin_result

        capability_result = self._validate_name(
            capability_name,
            "اسم الـCapability",
        )
        if not capability_result.success:
            return capability_result

        plugin = plugin_result.data
        name = capability_result.data

        if plugin not in self._capabilities:
            return Result.fail(
                message=f"الـPlugin غير موجود: {plugin}",
                metadata={
                    "plugin": plugin,
                    "capability": name,
                },
            )

        plugin_capabilities = self._capabilities[plugin]

        if name not in plugin_capabilities:
            return Result.fail(
                message=(
                    f"الـCapability غير مسجلة: "
                    f"{plugin}:{name}"
                ),
                metadata={
                    "plugin": plugin,
                    "capability": name,
                },
            )

        capability = plugin_capabilities.pop(name)

        if not plugin_capabilities:
            del self._capabilities[plugin]

        return Result.ok(
            data=capability,
            message=(
                f"تمت إزالة الـCapability: "
                f"{plugin}:{name}"
            ),
            metadata={
                "plugin": plugin,
                "capability": name,
            },
        )

    @staticmethod
    def _validate_name(
        value: str,
        field_name: str,
    ) -> Result:
        """
        Validate a public name argument.
        """
        if not isinstance(value, str):
            return Result.fail(
                message=f"{field_name} غير صالح.",
            )

        normalized = value.strip()

        if not normalized:
            return Result.fail(
                message=f"{field_name} غير صالح.",
            )

        return Result.ok(
            data=normalized,
        )