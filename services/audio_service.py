"""Provider-neutral audio service boundary for v0.7."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


# --------------------------------------------------
# Provider Protocols
# --------------------------------------------------


class AudioInterpreter(Protocol):
    def interpret(self, instruction: str) -> Result:
        ...


class SpeechToTextProvider(Protocol):
    """Provider boundary for speech-to-text transcription."""

    def transcribe(
        self,
        source: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        ...


class TextToSpeechProvider(Protocol):
    """Provider boundary for text-to-speech synthesis."""

    def synthesize(
        self,
        text: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        ...


# --------------------------------------------------
# Audio Service
# --------------------------------------------------


class AudioService:
    """Service boundary for audio operations."""

    _OPERATIONS = frozenset({"transcribe", "speak", "create_plan"})

    def __init__(
        self,
        interpreter: AudioInterpreter | None = None,
        stt_provider: SpeechToTextProvider | None = None,
        tts_provider: TextToSpeechProvider | None = None,
    ) -> None:
        self._interpreter = interpreter
        self._stt_provider = stt_provider
        self._tts_provider = tts_provider

    def execute(self, command: str) -> Result:
        """Main entry point for audio commands."""
        if not isinstance(command, str) or not command.strip():
            return Result.fail("Audio command is invalid.")

        body = command.strip()
        parts = body.split(maxsplit=1)
        operation = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if operation == "transcribe":
            return self.transcribe(args)
        if operation == "speak":
            return self.speak(args)
        if operation == "create_plan":
            return self.create_plan(args)

        return Result.fail(
            f"Unsupported audio operation: {operation}. "
            f"Supported: {', '.join(sorted(self._OPERATIONS))}"
        )

    # --------------------------------------------------
    # Speech-to-Text
    # --------------------------------------------------

    def transcribe(
        self,
        source: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(source, str) or not source.strip():
            return Result.fail("Transcription source is invalid.")

        if self._stt_provider is None:
            return Result.fail("No speech-to-text provider is registered.")

        transcribe_fn = getattr(self._stt_provider, "transcribe", None)
        if not callable(transcribe_fn):
            return Result.fail("Speech-to-text provider is invalid.")

        try:
            result = transcribe_fn(source.strip(), parameters)
        except Exception:
            return Result.fail("Speech-to-text provider execution failed.")

        if not isinstance(result, Result):
            return Result.fail(
                "Speech-to-text provider returned an invalid Result."
            )

        return result

    # --------------------------------------------------
    # Text-to-Speech
    # --------------------------------------------------

    def speak(
        self,
        text: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(text, str) or not text.strip():
            return Result.fail("Speech text is invalid.")

        if self._tts_provider is None:
            return Result.fail("No text-to-speech provider is registered.")

        synthesize_fn = getattr(self._tts_provider, "synthesize", None)
        if not callable(synthesize_fn):
            return Result.fail("Text-to-speech provider is invalid.")

        try:
            result = synthesize_fn(text.strip(), parameters)
        except Exception:
            return Result.fail("Text-to-speech provider execution failed.")

        if not isinstance(result, Result):
            return Result.fail(
                "Text-to-speech provider returned an invalid Result."
            )

        return result

    # --------------------------------------------------
    # Audio Plan (legacy v0.9 path)
    # --------------------------------------------------

    def create_plan(self, instruction: str) -> Result:
        if not isinstance(instruction, str) or not instruction.strip():
            return Result.fail("Audio instruction is invalid.")
        if self._interpreter is None:
            return Result.fail("No audio interpreter is registered.")
        interpret = getattr(self._interpreter, "interpret", None)
        if not callable(interpret):
            return Result.fail("Audio interpreter is invalid.")
        try:
            result = interpret(instruction.strip())
        except Exception:
            return Result.fail("Audio interpreter execution failed.")
        if not isinstance(result, Result) or not result.success:
            return Result.fail("Audio interpreter failed.")
        tracks = self._normalize_tracks(result.data)
        if tracks is None:
            return Result.fail("Audio plan is malformed.")
        return Result.ok(
            data={"tracks": tracks},
            message="Audio plan validated successfully.",
            metadata={"track_count": len(tracks)},
        )

    @staticmethod
    def _normalize_tracks(data: Any) -> list[dict[str, Any]] | None:
        if not isinstance(data, Mapping):
            return None
        tracks = data.get("tracks")
        if isinstance(tracks, (str, bytes)) or not isinstance(tracks, Sequence):
            return None
        normalized: list[dict[str, Any]] = []
        identifiers: set[str] = set()
        for track in tracks:
            if not isinstance(track, Mapping):
                return None
            identifier = track.get("id")
            start = track.get("start")
            duration = track.get("duration")
            kind = track.get("kind")
            continuity = track.get("continuity")
            if not isinstance(identifier, str) or not identifier.strip():
                return None
            if identifier.strip() in identifiers:
                return None
            if not isinstance(start, (int, float)) or start < 0:
                return None
            if not isinstance(duration, (int, float)) or duration <= 0:
                return None
            if not isinstance(kind, str) or not kind.strip():
                return None
            if not isinstance(continuity, Mapping):
                return None
            item = dict(track)
            item.update(
                id=identifier.strip(),
                start=float(start),
                duration=float(duration),
                kind=kind.strip(),
            )
            normalized.append(item)
            identifiers.add(identifier.strip())
        if not normalized:
            return None
        return normalized
