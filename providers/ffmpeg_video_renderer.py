"""FFmpeg implementation of the VideoRenderer Protocol for v0.8.

Uses local FFmpeg binary for deterministic video rendering/composition.
Operates on the validated video plan structure from VideoProductionService.

FFmpeg must be available on PATH or at the configured path.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Any

from core.result import Result

_DEFAULT_FFMPEG_PATH = "ffmpeg"
_DEFAULT_TIMEOUT_SECONDS = 120


def _resolve_ffmpeg_path() -> str | None:
    import shutil
    path = shutil.which(_DEFAULT_FFMPEG_PATH)
    return path if path else None


def _validate_plan(plan: dict[str, Any]) -> str | None:
    """Validate that plan has the minimum required structure for rendering.
    Returns error message or None if valid."""
    if not isinstance(plan, dict):
        return "Render plan must be a dict."

    timeline = plan.get("timeline")
    if isinstance(timeline, (str, bytes)) or not isinstance(timeline, list):
        return "Render plan timeline is invalid."

    if not timeline:
        return "Render plan timeline is empty."

    for i, stage in enumerate(timeline):
        if not isinstance(stage, dict):
            return f"Stage {i} is not a dict."
        stage_id = stage.get("id")
        if not isinstance(stage_id, str) or not stage_id.strip():
            return f"Stage {i} has no valid id."
        scenes = stage.get("scenes")
        if isinstance(scenes, (str, bytes)) or not isinstance(scenes, list):
            return f"Stage {i} scenes are invalid."
        if not scenes:
            return f"Stage {i} has no scenes."

        for j, scene in enumerate(scenes):
            if not isinstance(scene, dict):
                return f"Stage {i} scene {j} is not a dict."
            scene_id = scene.get("id")
            if not isinstance(scene_id, str) or not scene_id.strip():
                return f"Stage {i} scene {j} has no valid id."

    return None


class FFmpegVideoRenderer:
    """Provider-owned FFmpeg video rendering adapter.

    Conforms to VideoRenderer Protocol:
        render(plan, parameters) -> Result
    """

    def __init__(
        self,
        ffmpeg_path: str | None = None,
        output_dir: str | None = None,
    ) -> None:
        self._ffmpeg_path = ffmpeg_path
        self._output_dir = output_dir

    def render(
        self,
        plan: dict[str, Any],
        parameters: dict[str, Any] | None = None,
    ) -> Result:
        if not isinstance(plan, dict):
            return Result.fail("Render plan is invalid.")

        validation_error = _validate_plan(plan)
        if validation_error is not None:
            return Result.fail(validation_error)

        params = dict(parameters) if isinstance(parameters, dict) else {}

        ffmpeg_path = self._ffmpeg_path or _resolve_ffmpeg_path()
        if not ffmpeg_path:
            return Result.fail("FFmpeg is not available on the system.")

        output_dir = self._output_dir or tempfile.gettempdir()
        output_path = os.path.join(output_dir, _build_output_filename(plan))

        timeline = plan.get("timeline", [])
        video_files = _collect_video_files(timeline)

        if not video_files:
            return Result.fail("No video files found in the render plan.")

        existing_files = [f for f in video_files if os.path.isfile(f)]
        if not existing_files:
            return Result.fail("No existing video files found on disk.")

        concat_list = _write_concat_list(existing_files, output_dir)
        if concat_list is None:
            return Result.fail("Failed to create concat list.")

        timeout = int(params.get("timeout", _DEFAULT_TIMEOUT_SECONDS))

        cmd = [
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            output_path,
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            return Result.fail("FFmpeg rendering timed out.")
        except FileNotFoundError:
            return Result.fail("FFmpeg executable not found.")
        except Exception:
            return Result.fail("FFmpeg rendering execution failed.")
        finally:
            _cleanup_concat_list(concat_list)

        if proc.returncode != 0:
            stderr_msg = _truncate_error(proc.stderr)
            return Result.fail(f"FFmpeg rendering failed: {stderr_msg}")

        if not os.path.isfile(output_path):
            return Result.fail("FFmpeg produced no output file.")

        file_size = _get_file_size(output_path)

        return Result.ok(
            data={
                "path": output_path,
                "format": "mp4",
                "size_bytes": file_size,
                "provider": "ffmpeg",
                "input_files": len(existing_files),
            },
            message="Video rendered successfully.",
            metadata={
                "provider": "ffmpeg",
                "command": " ".join(cmd),
                "timeout": timeout,
            },
        )


def _build_output_filename(plan: dict[str, Any]) -> str:
    stages = plan.get("timeline", [])
    stage_ids = [s.get("id", "x") for s in stages if isinstance(s, dict)]
    suffix = "_".join(stage_ids[:3]) if stage_ids else "render"
    safe = "".join(c if c.isalnum() or c == "_" else "_" for c in suffix)
    return f"render_{safe}.mp4"


def _collect_video_files(timeline: list[dict[str, Any]]) -> list[str]:
    """Extract video file paths from the plan timeline scenes."""
    files: list[str] = []
    for stage in timeline:
        if not isinstance(stage, dict):
            continue
        scenes = stage.get("scenes", [])
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            video_ref = scene.get("video")
            if isinstance(video_ref, str) and video_ref.strip():
                files.append(video_ref.strip())
            elif isinstance(video_ref, dict):
                path = video_ref.get("path") or video_ref.get("uri")
                if isinstance(path, str) and path.strip():
                    files.append(path.strip())
    return files


def _write_concat_list(files: list[str], output_dir: str) -> str | None:
    """Write an FFmpeg concat demuxer list file."""
    try:
        fd, path = tempfile.mkstemp(suffix=".txt", dir=output_dir, prefix="concat_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for video_file in files:
                safe_path = video_file.replace("'", "'\\''")
                f.write(f"file '{safe_path}'\n")
        return path
    except Exception:
        return None


def _cleanup_concat_list(path: str) -> None:
    try:
        if os.path.isfile(path):
            os.remove(path)
    except Exception:
        pass


def _get_file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except Exception:
        return 0


def _truncate_error(stderr: str, max_len: int = 500) -> str:
    if not stderr:
        return "unknown error"
    trimmed = stderr.strip()
    if len(trimmed) > max_len:
        return trimmed[:max_len] + "..."
    return trimmed
