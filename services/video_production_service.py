"""Temporal video production planning boundary for v0.9."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


class VideoInterpreter(Protocol):
    """Optional injected temporal instruction interpreter."""

    def interpret(self, instruction: str) -> Result:
        ...


class VideoProductionService:
    """Validate temporal production plans without rendering media."""

    def __init__(self, interpreter: VideoInterpreter | None = None) -> None:
        self._interpreter = interpreter

    def create_plan(self, instruction: str) -> Result:
        if not isinstance(instruction, str) or not instruction.strip():
            return Result.fail("Video instruction is invalid.")
        if self._interpreter is None:
            return Result.fail("No video interpreter is registered.")

        interpret = getattr(self._interpreter, "interpret", None)
        if not callable(interpret):
            return Result.fail("Video interpreter is invalid.")

        try:
            result = interpret(instruction.strip())
        except Exception:
            return Result.fail("Video interpreter execution failed.")
        if not isinstance(result, Result) or not result.success:
            return Result.fail("Video interpreter failed.")
        if not isinstance(result.data, Mapping):
            return Result.fail("Video interpreter returned malformed data.")

        normalized = self._normalize_plan(result.data)
        if normalized is None:
            return Result.fail("Video temporal plan is malformed.")

        stage_count = len(normalized["timeline"])
        scene_count = sum(len(stage["scenes"]) for stage in normalized["timeline"])
        return Result.ok(
            data=normalized,
            message="Temporal video plan validated successfully.",
            metadata={"stage_count": stage_count, "scene_count": scene_count},
        )

    @staticmethod
    def _normalize_plan(data: Mapping[str, Any]) -> dict[str, Any] | None:
        timeline = data.get("timeline")
        if isinstance(timeline, (str, bytes)) or not isinstance(timeline, Sequence):
            return None

        stages: list[dict[str, Any]] = []
        stage_ids: set[str] = set()
        for stage in timeline:
            if not isinstance(stage, Mapping):
                return None
            stage_id = stage.get("id")
            duration = stage.get("duration")
            scenes = stage.get("scenes")
            if not isinstance(stage_id, str) or not stage_id.strip():
                return None
            if stage_id.strip() in stage_ids:
                return None
            if not isinstance(duration, (int, float)) or duration <= 0:
                return None
            if isinstance(scenes, (str, bytes)) or not isinstance(scenes, Sequence):
                return None

            normalized_scenes: list[dict[str, Any]] = []
            scene_ids: set[str] = set()
            for scene in scenes:
                if not isinstance(scene, Mapping):
                    return None
                scene_id = scene.get("id")
                if not isinstance(scene_id, str) or not scene_id.strip():
                    return None
                if scene_id.strip() in scene_ids:
                    return None
                required = ("motion", "camera", "audio", "continuity")
                if any(not isinstance(scene.get(key), Mapping) for key in required):
                    return None
                normalized_scene = dict(scene)
                normalized_scene["id"] = scene_id.strip()
                normalized_scenes.append(normalized_scene)
                scene_ids.add(scene_id.strip())

            if not normalized_scenes:
                return None
            normalized_stage = dict(stage)
            normalized_stage["id"] = stage_id.strip()
            normalized_stage["duration"] = float(duration)
            normalized_stage["scenes"] = normalized_scenes
            stages.append(normalized_stage)
            stage_ids.add(stage_id.strip())

        if not stages:
            return None
        normalized = dict(data)
        normalized["timeline"] = stages
        return normalized
