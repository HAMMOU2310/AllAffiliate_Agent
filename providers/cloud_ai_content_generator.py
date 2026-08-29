"""
Thin adapter bridging CloudAIService to the ContentGenerator protocol.

No API keys. No SDK clients. No business logic.
Delegates all AI execution to CloudAIService.
"""

from __future__ import annotations

from typing import Any

from core.result import Result


class CloudAIContentGenerator:
    """Adapter: CloudAIService → ContentGenerator protocol."""

    def __init__(
        self,
        cloud_ai_service: Any,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> None:
        self._service = cloud_ai_service
        self._model = model
        self._parameters = parameters

    def generate(
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

        if self._service is None:
            return Result.fail("No Cloud AI service is registered.")

        generate = getattr(self._service, "generate", None)
        if not callable(generate):
            return Result.fail("Cloud AI service is invalid.")

        prompt = self._build_prompt(
            brief.strip(),
            persona,
            format.strip() if isinstance(format, str) else None,
        )

        try:
            result = generate(
                prompt=prompt,
                model=self._model,
                parameters=self._parameters,
            )
        except Exception:
            return Result.fail("Cloud AI service execution failed.")

        if not isinstance(result, Result):
            return Result.fail("Cloud AI service returned an invalid Result.")

        if not result.success:
            return Result.fail(
                result.message or "Cloud AI service generation failed.",
                errors=result.errors,
                metadata=result.metadata,
            )

        draft = self._to_draft(result.data)
        if draft is None:
            return Result.fail("Cloud AI service returned malformed content.")

        return Result.ok(
            data=draft,
            message="Content generated successfully.",
            metadata={
                "model": self._model,
                "format": format.strip() if isinstance(format, str) else None,
            },
        )

    @staticmethod
    def _build_prompt(
        brief: str,
        persona: dict[str, Any] | None,
        format: str | None,
    ) -> str:
        parts = [
            "You are a professional content writer.",
            "",
            "Write content based on the following brief:",
            brief,
        ]

        if persona:
            parts.append("")
            parts.append("Audience and tone requirements:")
            for key, value in persona.items():
                parts.append(f"- {key}: {value}")

        if format:
            parts.append("")
            parts.append(f"Output format: {format}")

        parts.append("")
        parts.append("Return your response in this exact structure:")
        parts.append("TITLE: <one-line title>")
        parts.append("BODY: <the full content>")
        parts.append("CLAIMS: <semicolon-separated factual claims, or NONE>")

        return "\n".join(parts)

    @staticmethod
    def _to_draft(raw: Any) -> dict[str, Any] | None:
        if not isinstance(raw, str):
            return None

        title = ""
        body = ""
        claims: list[str] = []

        lines = raw.split("\n")
        section = None
        body_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            if stripped.upper().startswith("TITLE:"):
                title = stripped[6:].strip()
                section = "title"
                continue

            if stripped.upper().startswith("BODY:"):
                body = stripped[5:].strip()
                section = "body"
                continue

            if stripped.upper().startswith("CLAIMS:"):
                claims_text = stripped[7:].strip()
                if claims_text and claims_text.upper() != "NONE":
                    claims = [
                        c.strip()
                        for c in claims_text.split(";")
                        if c.strip()
                    ]
                section = "claims"
                continue

            if section == "body":
                body_lines.append(line)

        if body_lines and not body:
            body = "\n".join(body_lines).strip()
        elif body_lines:
            body = body + "\n" + "\n".join(body_lines).strip()

        if not title or not body:
            return None

        return {
            "title": title,
            "body": body.strip(),
            "claims": claims,
        }
