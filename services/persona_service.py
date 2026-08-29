"""Reusable content persona validation for v0.8."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.result import Result


class PersonaService:
    """Validate reusable content persona profiles."""

    _REQUIRED = {"audience", "language", "tone"}
    _OPTIONAL = {
        "storytelling_style",
        "narration_style",
        "visual_identity",
        "marketing_style",
        "cta_behavior",
        "platform_constraints",
        "prohibited_claims",
    }

    def validate(self, persona: dict[str, Any]) -> Result:
        if not isinstance(persona, dict):
            return Result.fail("Content persona is invalid.")
        if not self._REQUIRED.issubset(persona):
            return Result.fail("Content persona is missing required fields.")
        if any(
            not isinstance(persona[field], str) or not persona[field].strip()
            for field in self._REQUIRED
        ):
            return Result.fail("Content persona required fields are invalid.")

        unknown = set(persona) - self._REQUIRED - self._OPTIONAL
        if unknown:
            return Result.fail("Content persona contains unsupported fields.")

        normalized = dict(persona)
        for field in self._REQUIRED:
            normalized[field] = persona[field].strip()
        for field in self._OPTIONAL:
            if field in persona and not isinstance(persona[field], (str, list, dict)):
                return Result.fail("Content persona optional field is invalid.")
            if isinstance(persona.get(field), str):
                normalized[field] = persona[field].strip()
            elif isinstance(persona.get(field), list):
                normalized[field] = list(persona[field])
            elif isinstance(persona.get(field), Mapping):
                normalized[field] = dict(persona[field])

        return Result.ok(
            data=normalized,
            message="Content persona validated successfully.",
            metadata={"field_count": len(normalized)},
        )
