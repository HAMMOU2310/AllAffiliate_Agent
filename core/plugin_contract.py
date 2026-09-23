"""Plugin contract for AllAffiliate_Agent.

A plugin is a Python module in the plugins/ directory that defines
a Plugin class implementing this contract.
"""

from __future__ import annotations

from typing import Any, Protocol


class PluginContract(Protocol):
    """Minimal interface every plugin must satisfy."""

    @property
    def id(self) -> str:
        """Unique plugin identifier."""
        ...

    @property
    def name(self) -> str:
        """Human-readable plugin name."""
        ...

    def initialize(self, services: Any, router: Any = None) -> None:
        """Called once during application startup.

        Plugins register services via services.register() and
        agents via router.registry.register() if router is provided.
        """
        ...

    def shutdown(self) -> None:
        """Called once during application shutdown.

        Release any resources held by the plugin.
        """
        ...
