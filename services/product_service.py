"""Evidence-based product candidate ranking for v0.8."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from core.result import Result


class ProductService:
    """Rank candidates using the mean of at least two supplied signals."""

    def rank(self, candidates: Sequence[Mapping[str, Any]]) -> Result:
        if isinstance(candidates, (str, bytes)) or not isinstance(
            candidates, Sequence
        ):
            return Result.fail("Product candidates are invalid.")

        ranked: list[dict[str, Any]] = []
        identifiers: set[str] = set()
        for candidate in candidates:
            if not isinstance(candidate, Mapping):
                return Result.fail("Product candidate is invalid.")

            identifier = candidate.get("id")
            name = candidate.get("name")
            signals = candidate.get("signals")
            if not isinstance(identifier, str) or not identifier.strip():
                return Result.fail("Product candidate ID is invalid.")
            identifier = identifier.strip()
            if identifier in identifiers:
                return Result.fail("Product candidate IDs must be unique.")
            if not isinstance(name, str) or not name.strip():
                return Result.fail("Product candidate name is invalid.")
            if not isinstance(signals, Mapping) or len(signals) < 2:
                return Result.fail("At least two product signals are required.")

            normalized_signals: dict[str, float] = {}
            for key, value in signals.items():
                if not isinstance(key, str) or not key.strip():
                    return Result.fail("Product signal name is invalid.")
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    return Result.fail("Product signal value is invalid.")
                if not math.isfinite(float(value)):
                    return Result.fail("Product signal value is invalid.")
                normalized_signals[key.strip()] = float(value)

            identifiers.add(identifier)
            item = dict(candidate)
            item["id"] = identifier
            item["name"] = name.strip()
            item["signals"] = normalized_signals
            item["score"] = sum(normalized_signals.values()) / len(normalized_signals)
            item["signals_used"] = list(normalized_signals)
            ranked.append(item)

        ranked.sort(key=lambda item: (-item["score"], item["id"]))
        return Result.ok(
            data=ranked,
            message="Product candidates ranked successfully.",
            metadata={
                "candidate_count": len(ranked),
                "ranking_method": "arithmetic_mean_of_supplied_signals",
            },
        )
