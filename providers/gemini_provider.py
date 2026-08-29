"""
Google Gemini implementation of the provider-neutral CloudAIProvider contract.
"""

from __future__ import annotations

import os
from typing import Any

from core.result import Result

_DEFAULT_MODEL = "gemini-2.5-flash-lite"


def _create_gemini_client(api_key: str) -> Any:
    """Create the Google GenAI client without exposing provider credentials."""
    try:
        from google import genai
    except Exception as exc:
        raise RuntimeError("Google GenAI SDK is unavailable.") from exc

    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        raise RuntimeError("Gemini client configuration is invalid.") from exc


class GeminiProvider:
    """Provider-owned Google Gemini execution adapter."""

    def __init__(self) -> None:
        self._client: Any | None = None

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        parameters: dict | None = None,
    ) -> Result:
        if not isinstance(prompt, str) or not prompt.strip():
            return Result.fail("Prompt is invalid.")

        if model is not None and (
            not isinstance(model, str) or not model.strip()
        ):
            return Result.fail("Gemini model configuration is invalid.")

        if parameters is not None and not isinstance(parameters, dict):
            return Result.fail("Gemini parameters configuration is invalid.")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or not api_key.strip():
            return Result.fail("Gemini credentials are not configured.")

        resolved_model = model.strip() if isinstance(model, str) and model.strip() else _DEFAULT_MODEL

        request_parameters = self._validate_parameters(parameters)

        try:
            if self._client is None:
                self._client = _create_gemini_client(api_key)

            response = self._client.models.generate_content(
                model=resolved_model,
                contents=prompt.strip(),
                config=request_parameters,
            )
        except Exception:
            return Result.fail("Gemini generation failed.")

        content = self._extract_content(response)
        if content is None:
            return Result.fail("Gemini returned an invalid response.")

        return Result.ok(
            data=content,
            message="Gemini generation completed successfully.",
        )

    @staticmethod
    def _validate_parameters(parameters: dict | None) -> dict | None:
        if parameters is None:
            return None

        if not isinstance(parameters, dict):
            return None

        blocked = {"model", "contents"}
        for key in blocked:
            if key in parameters:
                return None

        return dict(parameters)

    @staticmethod
    def _extract_content(response: Any) -> str | None:
        try:
            text = response.text
            if isinstance(text, str) and text.strip():
                return text.strip()
        except (AttributeError, TypeError):
            pass

        try:
            candidates = response.candidates
            if not candidates:
                return None

            parts = candidates[0].content.parts
            if not parts:
                return None

            text_parts = []
            for part in parts:
                if hasattr(part, "text") and isinstance(part.text, str):
                    text_parts.append(part.text)

            result = "\n".join(text_parts).strip()
            return result if result else None
        except (AttributeError, IndexError, TypeError):
            return None
