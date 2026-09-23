"""Provider-neutral video production service boundary for v0.8."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from core.result import Result


# --------------------------------------------------
# Provider Protocols
# --------------------------------------------------


class VideoInterpreter(Protocol):
    """Optional injected temporal instruction interpreter."""

    def interpret(self, instruction: str) -> Result:
        ...


class VideoGenerator(Protocol):
    """Provider boundary for AI video generation."""

    def generate(
        self,
        prompt: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        ...


class VideoRenderer(Protocol):
    """Provider boundary for video rendering/composition."""

    def render(
        self,
        plan: dict[str, Any],
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        ...


# --------------------------------------------------
# Video Production Service
# --------------------------------------------------


class VideoProductionService:
    """Service boundary for video operations."""

    _OPERATIONS = frozenset({"generate", "render", "create_plan"})

    def __init__(
        self,
        interpreter: VideoInterpreter | None = None,
        generator: VideoGenerator | None = None,
        renderer: VideoRenderer | None = None,
    ) -> None:
        self._interpreter = interpreter
        self._generator = generator
        self._renderer = renderer

    def execute(self, command: str) -> Result:
        """Main entry point for video commands."""
        if not isinstance(command, str) or not command.strip():
            return Result.fail("Video command is invalid.")

        body = command.strip()
        parts = body.split(maxsplit=1)
        operation = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if operation == "generate":
            return self.generate(args)
        if operation == "render":
            return self.render(args)
        if operation == "create_plan":
            return self.create_plan(args)

        return Result.fail(
            f"Unsupported video operation: {operation}. "
            f"Supported: {', '.join(sorted(self._OPERATIONS))}"
        )

    # --------------------------------------------------
    # Video Generation
    # --------------------------------------------------

    def generate(
        self,
        prompt: str,
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(prompt, str) or not prompt.strip():
            return Result.fail("Video prompt is invalid.")

        if self._generator is None:
            return Result.fail("No video generation provider is registered.")

        generate_fn = getattr(self._generator, "generate", None)
        if not callable(generate_fn):
            return Result.fail("Video generation provider is invalid.")

        try:
            result = generate_fn(prompt.strip(), parameters)
        except Exception:
            return Result.fail("Video generation provider execution failed.")

        if not isinstance(result, Result):
            return Result.fail(
                "Video generation provider returned an invalid Result."
            )

        return result

    # --------------------------------------------------
    # Video Rendering
    # --------------------------------------------------

    def render(
        self,
        plan: str | dict[str, Any],
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if isinstance(plan, str):
            plan = plan.strip()
            if not plan:
                return Result.fail("Video render plan is invalid.")
            try:
                import json
                plan = json.loads(plan)
            except (json.JSONDecodeError, ValueError):
                return Result.fail("Video render plan is not valid JSON.")

        if not isinstance(plan, dict):
            return Result.fail("Video render plan must be a dict or JSON string.")

        if self._renderer is None:
            return Result.fail("No video rendering provider is registered.")

        render_fn = getattr(self._renderer, "render", None)
        if not callable(render_fn):
            return Result.fail("Video rendering provider is invalid.")

        try:
            result = render_fn(plan, parameters)
        except Exception:
            return Result.fail("Video rendering provider execution failed.")

        if not isinstance(result, Result):
            return Result.fail(
                "Video rendering provider returned an invalid Result."
            )

        return result

    # --------------------------------------------------
    # Temporal Plan (legacy path)
    # --------------------------------------------------

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
