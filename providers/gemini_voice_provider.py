"""Gemini-based speech-to-text and text-to-speech providers for v0.7.

Uses google-genai SDK multimodal capabilities for audio transcription
and speech synthesis via the Gemini API.

GEMINI_API_KEY must be set in the environment.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from core.result import Result

_DEFAULT_STT_MODEL = "gemini-2.0-flash"
_DEFAULT_TTS_MODEL = "gemini-2.0-flash"
_DEFAULT_TTS_VOICE = "Kore"

_MIME_MAP = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".webm": "audio/webm",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
}


def _create_client(api_key: str) -> Any:
    try:
        from google import genai
    except Exception as exc:
        raise RuntimeError("Google GenAI SDK is unavailable.") from exc
    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        raise RuntimeError("Gemini client configuration is invalid.") from exc


def _get_mime_type(path_str: str) -> str:
    ext = Path(path_str).suffix.lower()
    return _MIME_MAP.get(ext, "audio/wav")


def _resolve_api_key() -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    return key.strip() if isinstance(key, str) and key.strip() else None


class GeminiSTTProvider:
    """Speech-to-text provider using Gemini multimodal audio understanding."""

    def __init__(self, model: str | None = None) -> None:
        self._model = model or _DEFAULT_STT_MODEL
        self._client: Any | None = None

    def transcribe(
        self,
        source: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(source, str) or not source.strip():
            return Result.fail("Transcription source is invalid.")

        source = source.strip()
        if not Path(source).exists():
            return Result.fail(f"Audio file not found: {source}")

        api_key = _resolve_api_key()
        if not api_key:
            return Result.fail("Gemini credentials are not configured.")

        params = dict(parameters or {}) if isinstance(parameters, dict) else {}
        language = params.get("language")
        prompt = params.get("prompt", "Transcribe this audio accurately.")

        try:
            audio_bytes = Path(source).read_bytes()
        except Exception:
            return Result.fail("Failed to read audio file.")

        if not audio_bytes:
            return Result.fail("Audio file is empty.")

        mime_type = _get_mime_type(source)

        try:
            from google import genai
            from google.genai import types

            if self._client is None:
                self._client = _create_client(api_key)

            audio_part = types.Part(
                inline_data=types.Blob(
                    data=audio_bytes,
                    mime_type=mime_type,
                )
            )

            config_kwargs: dict[str, Any] = {}
            if language:
                config_kwargs["audio_timestamp"] = True

            response = self._client.models.generate_content(
                model=self._model,
                contents=[audio_part, prompt],
                config=types.GenerateContentConfig(**config_kwargs)
                if config_kwargs
                else None,
            )
        except Exception:
            return Result.fail("Gemini transcription provider execution failed.")

        text = _extract_text(response)
        if text is None:
            return Result.fail("Gemini returned an empty transcription.")

        return Result.ok(
            data={
                "text": text,
                "provider": "gemini",
                "model": self._model,
                "source": source,
                "mime_type": mime_type,
            },
            message="Transcription completed successfully.",
            metadata={"provider": "gemini", "model": self._model},
        )


class GeminiTTSProvider:
    """Text-to-speech provider using Gemini speech synthesis."""

    def __init__(self, model: str | None = None) -> None:
        self._model = model or _DEFAULT_TTS_MODEL
        self._client: Any | None = None

    def synthesize(
        self,
        text: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(text, str) or not text.strip():
            return Result.fail("Speech text is invalid.")

        text = text.strip()

        api_key = _resolve_api_key()
        if not api_key:
            return Result.fail("Gemini credentials are not configured.")

        params = dict(parameters or {}) if isinstance(parameters, dict) else {}
        voice = params.get("voice", _DEFAULT_TTS_VOICE)
        output_path = params.get("output_path")
        language = params.get("language")

        try:
            from google import genai
            from google.genai import types

            if self._client is None:
                self._client = _create_client(api_key)

            speech_config = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice,
                    )
                ),
            )
            if language:
                speech_config.language_code = language

            response = self._client.models.generate_content(
                model=self._model,
                contents=text,
                config=types.GenerateContentConfig(
                    speech_config=speech_config,
                    response_modalities=["AUDIO"],
                ),
            )
        except Exception:
            return Result.fail("Gemini speech provider execution failed.")

        audio_data = _extract_audio(response)
        if audio_data is None:
            return Result.fail("Gemini returned no audio data.")

        audio_bytes = audio_data.get("data", b"")
        audio_mime = audio_data.get("mime_type", "audio/wav")

        if not audio_bytes:
            return Result.fail("Gemini returned empty audio data.")

        if output_path:
            try:
                out = Path(output_path)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(audio_bytes)
                saved_path = str(out)
            except Exception:
                return Result.fail("Failed to save audio file.")
        else:
            saved_path = None

        return Result.ok(
            data={
                "path": saved_path,
                "format": audio_mime.split("/")[-1] if "/" in audio_mime else "wav",
                "mime_type": audio_mime,
                "size_bytes": len(audio_bytes),
                "provider": "gemini",
                "model": self._model,
                "voice": voice,
                "text": text,
            },
            message="Speech synthesis completed successfully.",
            metadata={"provider": "gemini", "model": self._model, "voice": voice},
        )


# --------------------------------------------------
# Response extraction helpers
# --------------------------------------------------


def _extract_text(response: Any) -> str | None:
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
        texts = []
        for part in parts:
            if hasattr(part, "text") and isinstance(part.text, str):
                texts.append(part.text)
        result = "\n".join(texts).strip()
        return result if result else None
    except (AttributeError, IndexError, TypeError):
        return None


def _extract_audio(response: Any) -> dict[str, Any] | None:
    try:
        candidates = response.candidates
        if not candidates:
            return None
        parts = candidates[0].content.parts
        if not parts:
            return None
        for part in parts:
            inline = getattr(part, "inline_data", None)
            if inline is not None:
                data = getattr(inline, "data", None)
                mime = getattr(inline, "mime_type", "audio/wav")
                if data and isinstance(data, (bytes, bytearray)):
                    return {"data": bytes(data), "mime_type": mime}
    except (AttributeError, IndexError, TypeError):
        pass
    return None
