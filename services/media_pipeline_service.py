"""Provider-neutral media composition manifest validation for v0.9."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.result import Result


class MediaPipelineService:
    """Validate composition inputs without rendering or external calls."""

    def compose(self, video_plan: dict[str, Any], audio_plan: dict[str, Any]) -> Result:
        if not isinstance(video_plan, dict) or not isinstance(audio_plan, dict):
            return Result.fail("Media composition plans are invalid.")
        timeline = video_plan.get("timeline")
        tracks = audio_plan.get("tracks")
        if isinstance(timeline, (str, bytes)) or not isinstance(timeline, Sequence):
            return Result.fail("Video composition plan is invalid.")
        if isinstance(tracks, (str, bytes)) or not isinstance(tracks, Sequence):
            return Result.fail("Audio composition plan is invalid.")
        if not timeline or not tracks:
            return Result.fail("Media composition plans cannot be empty.")
        return Result.ok(
            data={
                "status": "VALIDATED",
                "video_plan": dict(video_plan),
                "audio_plan": dict(audio_plan),
            },
            message="Media composition manifest validated successfully.",
            metadata={"stage": "VALIDATED"},
        )
