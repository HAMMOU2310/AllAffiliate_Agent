"""Provider-neutral content intelligence boundary for v0.8."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from core.result import Result


class ContentGenerator(Protocol):
    """Optional injected content-generation boundary."""

    def generate(
        self,
        brief: str,
        persona: dict[str, Any] | None = None,
        format: str | None = None,
    ) -> Result:
        ...


class ContentService:
    """Validate structured drafts without publishing or policy decisions."""

    def __init__(self, generator: ContentGenerator | None = None) -> None:
        self._generator = generator

    def create(
        self,
        brief: str,
        persona: dict[str, Any] | None = None,
        format: str | None = None,
    ) -> Result:
        if not isinstance(brief, str) or not brief.strip():
            return Result.fail("Content brief is invalid.")
        if persona is not None and not isinstance(persona, dict):
            return Result.fail("Content persona is invalid.")
        if format is not None and (
            not isinstance(format, str) or not format.strip()
        ):
            return Result.fail("Content format is invalid.")
        if self._generator is None:
            return Result.fail("No content generator is registered.")

        generate = getattr(self._generator, "generate", None)
        if not callable(generate):
            return Result.fail("Content generator is invalid.")

        try:
            result = generate(
                brief.strip(),
                persona,
                format.strip() if isinstance(format, str) else None,
            )
        except Exception:
            return Result.fail("Content generator execution failed.")

        if not isinstance(result, Result) or not result.success:
            return Result.fail("Content generator failed.")

        draft = self._normalize_draft(result.data)
        if draft is None:
            return Result.fail("Content generator returned a malformed draft.")

        return Result.ok(
            data=draft,
            message="Content draft validated successfully.",
            metadata={
                "format": format.strip() if isinstance(format, str) else None,
                "claim_count": len(draft["claims"]),
            },
        )

    @staticmethod
    def _normalize_draft(data: Any) -> dict[str, Any] | None:
        if not isinstance(data, Mapping):
            return None
        title = data.get("title")
        body = data.get("body")
        claims = data.get("claims")
        if not isinstance(title, str) or not title.strip():
            return None
        if not isinstance(body, str) or not body.strip():
            return None
        if not isinstance(claims, list):
            return None
        if any(not isinstance(claim, str) or not claim.strip() for claim in claims):
            return None

        normalized = dict(data)
        normalized["title"] = title.strip()
        normalized["body"] = body.strip()
        normalized["claims"] = [claim.strip() for claim in claims]
        return normalized
