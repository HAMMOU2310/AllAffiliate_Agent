"""Generic experiment lifecycle storage for v0.9."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any
from core.result import Result


class ExperimentService:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}
        self._next_id = 1

    def create(self, asset_id: str, hypothesis: str, action: str) -> Result:
        if not all(isinstance(x, str) and x.strip() for x in (asset_id, hypothesis, action)):
            return Result.fail("Experiment input is invalid.")
        experiment_id = f"experiment-{self._next_id}"
        self._next_id += 1
        item = {"id": experiment_id, "asset_id": asset_id.strip(),
                "hypothesis": hypothesis.strip(), "action": action.strip(),
                "state": "EXPERIMENT", "measurements": [],
                "created_at": datetime.now(timezone.utc).isoformat()}
        self._items[experiment_id] = item
        return Result.ok(data=dict(item), message="Experiment created successfully.")

    def record_measurement(self, experiment_id: str, metrics: dict[str, int | float]) -> Result:
        item = self._items.get(experiment_id) if isinstance(experiment_id, str) else None
        if item is None:
            return Result.fail("Experiment is not registered.")
        if not isinstance(metrics, dict) or not metrics or any(
            not isinstance(k, str) or not k.strip() or not isinstance(v, (int, float))
            or isinstance(v, bool) or not math.isfinite(float(v)) for k, v in metrics.items()
        ):
            return Result.fail("Experiment metrics are invalid.")
        measurement = {k.strip(): float(v) for k, v in metrics.items()}
        item["measurements"].append(measurement)
        return Result.ok(data=dict(item), message="Experiment measurement recorded successfully.")

    def complete(self, experiment_id: str, result: str, learning: str | None = None) -> Result:
        item = self._items.get(experiment_id) if isinstance(experiment_id, str) else None
        if item is None:
            return Result.fail("Experiment is not registered.")
        if not isinstance(result, str) or not result.strip():
            return Result.fail("Experiment result is invalid.")
        if learning is not None and (not isinstance(learning, str) or not learning.strip()):
            return Result.fail("Experiment learning is invalid.")
        item.update(state="RESULT", result=result.strip(), learning=learning.strip() if learning else None)
        return Result.ok(data=dict(item), message="Experiment completed successfully.")

    def get(self, experiment_id: str) -> Result:
        item = self._items.get(experiment_id) if isinstance(experiment_id, str) else None
        if item is None:
            return Result.fail("Experiment is not registered.")
        return Result.ok(data=dict(item), message="Experiment retrieved successfully.")
