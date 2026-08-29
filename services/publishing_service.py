"""Provider/platform-neutral publishing gateway for v0.9."""

from __future__ import annotations

from typing import Any, Protocol

from core.result import Result


class PublishingAdapter(Protocol):
    def publish(self, asset: dict[str, Any], destination: str) -> Result:
        ...


class PublishingService:
    """Publish through an adapter while failing closed on blocked assets."""

    def __init__(self, adapter: PublishingAdapter | None = None) -> None:
        self._adapter = adapter

    def publish(self, asset: dict[str, Any], destination: str) -> Result:
        if not isinstance(asset, dict) or not asset:
            return Result.fail("Publish asset is invalid.")
        if not isinstance(destination, str) or not destination.strip():
            return Result.fail("Publish destination is invalid.")
        policy = asset.get("policy")
        if isinstance(policy, dict) and str(policy.get("decision", "")).upper() == "BLOCKED":
            return Result.fail("Publishing blocked by policy.")
        if self._adapter is None:
            return Result.fail("No publishing adapter is registered.")
        publish = getattr(self._adapter, "publish", None)
        if not callable(publish):
            return Result.fail("Publishing adapter is invalid.")
        try:
            result = publish(dict(asset), destination.strip())
        except Exception:
            return Result.fail("Publishing adapter execution failed.")
        if not isinstance(result, Result) or not result.success:
            return Result.fail("Publishing adapter failed.")
        return Result.ok(
            data=result.data,
            message="Asset published successfully.",
            metadata={"destination": destination.strip()},
        )
