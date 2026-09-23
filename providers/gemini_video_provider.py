"""Google Gemini implementation of the VideoGenerator Protocol for v0.8.

Uses google-genai SDK video generation via client.models.generate_videos().
Video generation is a long-running operation: submit → poll → extract video bytes.

GEMINI_API_KEY must be set in the environment.
"""

from __future__ import annotations

import os
import tempfile
import time
from typing import Any

from core.result import Result

_DEFAULT_MODEL = "veo-2.0-generate-001"
_POLL_INTERVAL_SECONDS = 5
_MAX_POLL_ATTEMPTS = 60  # 5s × 60 = 300s max wait


def _create_client(api_key: str) -> Any:
    try:
        from google import genai
    except Exception as exc:
        raise RuntimeError("Google GenAI SDK is unavailable.") from exc
    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        raise RuntimeError("Gemini client configuration is invalid.") from exc


def _resolve_api_key() -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    return key.strip() if isinstance(key, str) and key.strip() else None


class GeminiVideoProvider:
    """Provider-owned Google Gemini video generation adapter.

    Conforms to VideoGenerator Protocol:
        generate(prompt, parameters) -> Result
    """

    def __init__(self, output_dir: str | None = None) -> None:
        self._client: Any | None = None
        self._output_dir = output_dir

    def generate(
        self,
        prompt: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(prompt, str) or not prompt.strip():
            return Result.fail("Video prompt is invalid.")

        if parameters is not None and not isinstance(parameters, dict):
            return Result.fail("Gemini video parameters are invalid.")

        api_key = _resolve_api_key()
        if not api_key:
            return Result.fail("Gemini credentials are not configured.")

        params = dict(parameters) if isinstance(parameters, dict) else {}
        resolved_model = str(params.pop("model", _DEFAULT_MODEL))

        try:
            if self._client is None:
                self._client = _create_client(api_key)

            config = self._build_config(params)
            kwargs: dict[str, Any] = {
                "model": resolved_model,
                "prompt": prompt.strip(),
            }
            if config is not None:
                kwargs["config"] = config

            operation = self._client.models.generate_videos(**kwargs)
        except Exception:
            return Result.fail("Gemini video generation request failed.")

        completed = self._poll_until_done(operation)
        if completed is None:
            return Result.fail("Gemini video generation timed out.")

        if hasattr(completed, "error") and completed.error:
            return Result.fail("Gemini video generation failed remotely.")

        video_data = self._extract_video(completed)
        if video_data is None:
            return Result.fail("Gemini returned no generated video.")

        video_bytes, mime_type, video_uri = video_data
        fmt = _mime_to_format(mime_type)

        if not video_bytes:
            return Result.fail("Gemini returned empty video data.")

        output_dir = self._output_dir or tempfile.gettempdir()
        filename = f"gemini_video_{hash(prompt) & 0xFFFFFFFF:08x}.{fmt}"
        output_path = os.path.join(output_dir, filename)

        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(video_bytes)
        except Exception:
            return Result.fail("Failed to save generated video.")

        return Result.ok(
            data={
                "path": output_path,
                "format": fmt,
                "mime_type": mime_type,
                "size_bytes": len(video_bytes),
                "provider": "gemini",
                "uri": video_uri,
            },
            message="Video generated successfully.",
            metadata={
                "provider": "gemini",
                "model": resolved_model,
                "prompt": prompt.strip(),
            },
        )

    def _poll_until_done(self, operation: Any) -> Any:
        """Poll the long-running operation until done or timeout."""
        max_attempts = _MAX_POLL_ATTEMPTS
        try:
            poll_interval = float(_POLL_INTERVAL_SECONDS)
        except Exception:
            poll_interval = 5.0

        for _ in range(max_attempts):
            done_flag = getattr(operation, "done", None)
            if done_flag is True:
                return operation

            try:
                time.sleep(poll_interval)
            except Exception:
                return None

            try:
                operation = self._client.operations.get(operation)
            except Exception:
                return None

        done_flag = getattr(operation, "done", None)
        return operation if done_flag is True else None

    @staticmethod
    def _extract_video(
        operation: Any,
    ) -> tuple[bytes, str, str | None] | None:
        """Extract video bytes, MIME type, and URI from completed operation."""
        response = getattr(operation, "response", None)
        if response is None:
            response = getattr(operation, "result", None)
        if response is None:
            return None

        generated_videos = getattr(response, "generated_videos", None)
        if not generated_videos or not isinstance(generated_videos, list):
            return None

        first = generated_videos[0]
        video = getattr(first, "video", None)
        if video is None:
            return None

        video_bytes = getattr(video, "video_bytes", None)
        mime_type = getattr(video, "mime_type", "video/mp4") or "video/mp4"
        uri = getattr(video, "uri", None)

        if isinstance(video_bytes, (bytes, bytearray)) and video_bytes:
            return bytes(video_bytes), mime_type, uri

        if uri:
            return b"", mime_type, uri

        return None

    @staticmethod
    def _build_config(parameters: dict[str, Any]) -> Any:
        """Build GenerateVideosConfig from parameters dict."""
        if not parameters:
            return None

        try:
            from google.genai import types
        except Exception:
            return None

        config_fields: dict[str, Any] = {}
        field_map = {
            "number_of_videos": int,
            "fps": int,
            "duration_seconds": int,
            "seed": int,
            "aspect_ratio": str,
            "resolution": str,
            "person_generation": str,
            "negative_prompt": str,
            "enhance_prompt": bool,
            "generate_audio": bool,
            "output_gcs_uri": str,
        }

        for key, expected_type in field_map.items():
            if key in parameters:
                val = parameters[key]
                if isinstance(val, expected_type):
                    config_fields[key] = val

        if not config_fields:
            return None

        try:
            return types.GenerateVideosConfig(**config_fields)
        except Exception:
            return None


def _mime_to_format(mime_type: str) -> str:
    mapping = {
        "video/mp4": "mp4",
        "video/webm": "webm",
        "video/ogg": "ogg",
        "video/quicktime": "mov",
        "video/x-matroska": "mkv",
    }
    return mapping.get(mime_type.lower(), "mp4")
