"""Digital-asset performance observation storage for v0.9."""

from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any

from core.result import Result


class PerformanceMonitoringService:
    """Record numeric observations without inferring causes."""

    def __init__(self) -> None:
        self._observations: list[dict[str, Any]] = []
        self._next_id = 1

    def record(self, asset_id: str, metrics: dict[str, int | float]) -> Result:
        if not isinstance(asset_id, str) or not asset_id.strip():
            return Result.fail("Performance asset ID is invalid.")
        if not isinstance(metrics, dict) or not metrics:
            return Result.fail("Performance metrics are invalid.")
        if any(
            not isinstance(key, str)
            or not key.strip()
            or not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            for key, value in metrics.items()
        ):
            return Result.fail("Performance metrics contain invalid values.")

        observation = {
            "id": f"observation-{self._next_id}",
            "asset_id": asset_id.strip(),
            "metrics": {key.strip(): float(value) for key, value in metrics.items()},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._next_id += 1
        self._observations.append(observation)
        return Result.ok(
            data=dict(observation),
            message="Performance observation recorded successfully.",
            metadata={"observation_id": observation["id"]},
        )

    def list_observations(self, asset_id: str | None = None) -> Result:
        if asset_id is not None and (
            not isinstance(asset_id, str) or not asset_id.strip()
        ):
            return Result.fail("Performance asset ID is invalid.")
        normalized = asset_id.strip() if isinstance(asset_id, str) else None
        observations = [
            dict(observation)
            for observation in self._observations
            if normalized is None or observation["asset_id"] == normalized
        ]
        return Result.ok(
            data=observations,
            message="Performance observations listed successfully.",
            metadata={"count": len(observations), "asset_id": normalized},
        )
