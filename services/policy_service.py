"""Isolated policy decision boundary for v0.8."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from core.result import Result


class PolicyEvaluator(Protocol):
    """Optional injected policy evaluation boundary."""

    def evaluate(self, asset: dict[str, Any]) -> Result:
        ...


class PolicyService:
    """Normalize policy decisions without claiming religious authority."""

    _DECISIONS = {"ALLOWED", "BLOCKED", "REVIEW_REQUIRED"}

    def __init__(self, evaluator: PolicyEvaluator | None = None) -> None:
        self._evaluator = evaluator

    def evaluate(self, asset: dict[str, Any]) -> Result:
        if not isinstance(asset, dict) or not asset:
            return Result.fail("Policy asset is invalid.")
        if self._evaluator is None:
            return Result.fail("No policy evaluator is registered.")

        evaluate = getattr(self._evaluator, "evaluate", None)
        if not callable(evaluate):
            return Result.fail("Policy evaluator is invalid.")

        try:
            result = evaluate(dict(asset))
        except Exception:
            return Result.fail("Policy evaluator execution failed.")

        if not isinstance(result, Result) or not result.success:
            return Result.fail("Policy evaluator failed.")
        if not isinstance(result.data, Mapping):
            return Result.fail("Policy evaluator returned malformed data.")

        decision = result.data.get("decision")
        reasons = result.data.get("reasons")
        if not isinstance(decision, str) or decision.strip().upper() not in self._DECISIONS:
            return Result.fail("Policy decision is invalid.")
        if not isinstance(reasons, list) or any(
            not isinstance(reason, str) or not reason.strip() for reason in reasons
        ):
            return Result.fail("Policy reasons are invalid.")

        normalized_decision = decision.strip().upper()
        return Result.ok(
            data={
                "decision": normalized_decision,
                "reasons": [reason.strip() for reason in reasons],
                "publishable": normalized_decision == "ALLOWED",
            },
            message="Policy decision evaluated successfully.",
            metadata={"decision": normalized_decision},
        )
