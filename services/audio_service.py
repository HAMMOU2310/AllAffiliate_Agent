"""Separable audio planning boundary for v0.9."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


class AudioInterpreter(Protocol):
    def interpret(self, instruction: str) -> Result:
        ...


class AudioService:
    """Validate timed audio tracks without rendering them."""

    def __init__(self, interpreter: AudioInterpreter | None = None) -> None:
        self._interpreter = interpreter

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
