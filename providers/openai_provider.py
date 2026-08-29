"""
OpenAI implementation of the provider-neutral CloudAIProvider contract.
"""

from __future__ import annotations

import os
from typing import Any

from core.result import Result


def _create_openai_client(api_key: str) -> Any:
    """Create the OpenAI SDK client without exposing provider credentials."""
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError("OpenAI SDK is unavailable.") from exc

    try:
        return OpenAI(api_key=api_key)
    except Exception as exc:
        raise RuntimeError("OpenAI client configuration is invalid.") from exc


class OpenAIProvider:
    """Provider-owned OpenAI execution adapter."""

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
            return Result.fail("OpenAI model configuration is invalid.")

        if parameters is not None and not isinstance(parameters, dict):
            return Result.fail("OpenAI parameters configuration is invalid.")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or not api_key.strip():
            return Result.fail("OpenAI credentials are not configured.")

        if model is None:
            return Result.fail("OpenAI model configuration is missing.")

        request_parameters = dict(parameters or {})
        if "model" in request_parameters or "messages" in request_parameters:
            return Result.fail("OpenAI request configuration is invalid.")

        try:
            if self._client is None:
                self._client = _create_openai_client(api_key)

            response = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **request_parameters,
            )
        except Exception:
            return Result.fail("OpenAI generation failed.")

        content = self._extract_content(response)
        if content is None:
            return Result.fail("OpenAI returned an invalid response.")

        return Result.ok(
            data=content,
            message="OpenAI generation completed successfully.",
        )

    @staticmethod
    def _extract_content(response: Any) -> str | None:
        try:
            choices = response.choices
            if not choices:
                return None

            content = choices[0].message.content
            return content if isinstance(content, str) else None
        except (AttributeError, IndexError, TypeError):
            return None
