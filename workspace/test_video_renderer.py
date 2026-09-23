"""Unit tests for FFmpegVideoRenderer — mocked subprocess, no real rendering."""

from __future__ import annotations

import os
import tempfile
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from core.result import Result

VALID_PLAN = {
    "timeline": [
        {
            "id": "stage1",
            "duration": 5.0,
            "scenes": [
                {
                    "id": "scene1",
                    "video": "/tmp/video1.mp4",
                    "motion": {"event": "fade_in"},
                    "camera": {"shot": "wide"},
                    "audio": {"track": "music"},
                    "continuity": {"previous": None},
                },
                {
                    "id": "scene2",
                    "video": "/tmp/video2.mp4",
                    "motion": {"event": "pan"},
                    "camera": {"shot": "close"},
                    "audio": {"track": "voice"},
                    "continuity": {"previous": "scene1"},
                },
            ],
        }
    ]
}

PLAN_NO_VIDEO_FILES = {
    "timeline": [
        {
            "id": "stage1",
            "duration": 5.0,
            "scenes": [
                {
                    "id": "scene1",
                    "motion": {"event": "fade"},
                    "camera": {"shot": "wide"},
                    "audio": {"track": "none"},
                    "continuity": {"previous": None},
                }
            ],
        }
    ]
}

PLAN_DICT_VIDEO_REF = {
    "timeline": [
        {
            "id": "stage1",
            "duration": 5.0,
            "scenes": [
                {
                    "id": "scene1",
                    "video": {"path": "/tmp/video1.mp4"},
                    "motion": {"event": "fade"},
                    "camera": {"shot": "wide"},
                    "audio": {"track": "none"},
                    "continuity": {"previous": None},
                }
            ],
        }
    ]
}


# ── construction ─────────────────────────────────────────────────

class TestFFmpegVideoRendererConstruction:
    def test_construction_default(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        assert r._ffmpeg_path is None
        assert r._output_dir is None

    def test_construction_custom(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(ffmpeg_path="/usr/bin/ffmpeg", output_dir="/tmp/out")
        assert r._ffmpeg_path == "/usr/bin/ffmpeg"
        assert r._output_dir == "/tmp/out"


# ── plan validation ──────────────────────────────────────────────

class TestFFmpegVideoRendererPlanValidation:
    def test_render_non_dict_plan(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render("not a dict")
        assert not result.success
        assert "invalid" in result.message.lower()

    def test_render_list_plan(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render([1, 2, 3])
        assert not result.success

    def test_render_none_plan(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render(None)  # type: ignore
        assert not result.success

    def test_render_empty_timeline(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": []})
        assert not result.success
        assert "empty" in result.message.lower()

    def test_render_no_timeline(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"stages": []})
        assert not result.success

    def test_render_string_timeline(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": "bad"})
        assert not result.success

    def test_render_stage_not_dict(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": ["not_a_dict"]})
        assert not result.success

    def test_render_stage_no_id(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": [{"scenes": [{"id": "s"}]}]})
        assert not result.success

    def test_render_stage_empty_id(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": [{"id": "  ", "scenes": [{"id": "s"}]}]})
        assert not result.success

    def test_render_scene_not_dict(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": [{"id": "s1", "scenes": ["bad"]}]})
        assert not result.success

    def test_render_scene_no_id(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": [{"id": "s1", "scenes": [{"motion": {}}]}]})
        assert not result.success

    def test_render_empty_scenes(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": [{"id": "s1", "scenes": []}]})
        assert not result.success

    def test_render_scenes_not_list(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": [{"id": "s1", "scenes": "bad"}]})
        assert not result.success


# ── ffmpeg availability ──────────────────────────────────────────

class TestFFmpegVideoRendererAvailability:
    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value=None)
    def test_no_ffmpeg(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render(VALID_PLAN)
        assert not result.success
        assert "ffmpeg" in result.message.lower()


# ── video file collection ────────────────────────────────────────

class TestFFmpegVideoRendererFileCollection:
    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_no_video_files_in_plan(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render(PLAN_NO_VIDEO_FILES)
        assert not result.success
        assert "no video files" in result.message.lower()

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_no_existing_files_on_disk(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render(VALID_PLAN)
        assert not result.success
        assert "no existing" in result.message.lower()

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_dict_video_ref_collected(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        with patch("providers.ffmpeg_video_renderer.os.path.isfile", return_value=False):
            result = r.render(PLAN_DICT_VIDEO_REF)
            assert not result.success


# ── successful rendering ─────────────────────────────────────────

class TestFFmpegVideoRendererSuccess:
    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_render_success(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""
        with patch("providers.ffmpeg_video_renderer.subprocess.run", return_value=mock_proc):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "render_" in p or "video" in p):
                with patch("providers.ffmpeg_video_renderer.os.path.getsize", return_value=1024):
                    result = r.render(VALID_PLAN)
                    assert result.success
                    assert result.data["provider"] == "ffmpeg"
                    assert result.data["format"] == "mp4"
                    assert result.data["size_bytes"] == 1024

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_render_with_parameters(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""
        with patch("providers.ffmpeg_video_renderer.subprocess.run", return_value=mock_proc):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "render_" in p or "video" in p):
                with patch("providers.ffmpeg_video_renderer.os.path.getsize", return_value=2048):
                    result = r.render(VALID_PLAN, parameters={"timeout": 60})
                    assert result.success
                    assert result.data["input_files"] == 2

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_render_metadata(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""
        with patch("providers.ffmpeg_video_renderer.subprocess.run", return_value=mock_proc):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "render_" in p or "video" in p):
                with patch("providers.ffmpeg_video_renderer.os.path.getsize", return_value=512):
                    result = r.render(VALID_PLAN)
                    assert result.success
                    assert result.metadata["provider"] == "ffmpeg"
                    assert "timeout" in result.metadata


# ── subprocess failures ──────────────────────────────────────────

class TestFFmpegVideoRendererSubprocess:
    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_nonzero_exit_code(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "Invalid data found when processing input"
        with patch("providers.ffmpeg_video_renderer.subprocess.run", return_value=mock_proc):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "video" in p):
                result = r.render(VALID_PLAN)
                assert not result.success
                assert "failed" in result.message.lower()

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_timeout(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        import subprocess as sp
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        with patch("providers.ffmpeg_video_renderer.subprocess.run", side_effect=sp.TimeoutExpired(cmd="ffmpeg", timeout=60)):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "video" in p):
                result = r.render(VALID_PLAN)
                assert not result.success
                assert "timed out" in result.message.lower()

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_file_not_found(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        with patch("providers.ffmpeg_video_renderer.subprocess.run", side_effect=FileNotFoundError):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "video" in p):
                result = r.render(VALID_PLAN)
                assert not result.success
                assert "not found" in result.message.lower()

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_generic_exception(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        with patch("providers.ffmpeg_video_renderer.subprocess.run", side_effect=OSError("disk full")):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "video" in p):
                result = r.render(VALID_PLAN)
                assert not result.success
                assert "execution failed" in result.message.lower()

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_missing_output_file(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""
        with patch("providers.ffmpeg_video_renderer.subprocess.run", return_value=mock_proc):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "video" in p):
                result = r.render(VALID_PLAN)
                assert not result.success
                assert "no output" in result.message.lower()

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_long_stderr_truncated(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "x" * 1000
        with patch("providers.ffmpeg_video_renderer.subprocess.run", return_value=mock_proc):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "video" in p):
                result = r.render(VALID_PLAN)
                assert not result.success
                assert len(result.message) < 600


# ── protocol conformance ─────────────────────────────────────────

class TestFFmpegVideoRendererProtocolConformance:
    def test_has_render_method(self):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        assert callable(getattr(r, "render", None))

    def test_render_signature(self):
        import inspect
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer()
        sig = inspect.signature(r.render)
        params = list(sig.parameters.keys())
        assert "plan" in params
        assert "parameters" in params

    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_conforms_to_video_renderer(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        from services.video_production_service import VideoRenderer
        r = FFmpegVideoRenderer()
        result = r.render({"timeline": [{"id": "s", "scenes": [{"id": "x"}]}]})
        assert isinstance(result, Result)


# ── helper functions ─────────────────────────────────────────────

class TestFFmpegVideoRendererHelpers:
    def test_build_output_filename(self):
        from providers.ffmpeg_video_renderer import _build_output_filename
        plan = {"timeline": [{"id": "alpha"}, {"id": "beta"}]}
        name = _build_output_filename(plan)
        assert name.startswith("render_")
        assert name.endswith(".mp4")

    def test_build_output_filename_empty(self):
        from providers.ffmpeg_video_renderer import _build_output_filename
        name = _build_output_filename({"timeline": []})
        assert name == "render_render.mp4"

    def test_collect_video_files_string_ref(self):
        from providers.ffmpeg_video_renderer import _collect_video_files
        timeline = [{"scenes": [{"video": "/tmp/v.mp4"}]}]
        files = _collect_video_files(timeline)
        assert files == ["/tmp/v.mp4"]

    def test_collect_video_files_dict_ref(self):
        from providers.ffmpeg_video_renderer import _collect_video_files
        timeline = [{"scenes": [{"video": {"path": "/tmp/v.mp4"}}]}]
        files = _collect_video_files(timeline)
        assert files == ["/tmp/v.mp4"]

    def test_collect_video_files_uri_ref(self):
        from providers.ffmpeg_video_renderer import _collect_video_files
        timeline = [{"scenes": [{"video": {"uri": "/tmp/v.mp4"}}]}]
        files = _collect_video_files(timeline)
        assert files == ["/tmp/v.mp4"]

    def test_collect_video_files_empty(self):
        from providers.ffmpeg_video_renderer import _collect_video_files
        files = _collect_video_files([])
        assert files == []

    def test_collect_video_files_no_video_key(self):
        from providers.ffmpeg_video_renderer import _collect_video_files
        timeline = [{"scenes": [{"id": "s1"}]}]
        files = _collect_video_files(timeline)
        assert files == []

    def test_collect_video_files_whitespace_skipped(self):
        from providers.ffmpeg_video_renderer import _collect_video_files
        timeline = [{"scenes": [{"video": "  "}, {"video": "/tmp/v.mp4"}]}]
        files = _collect_video_files(timeline)
        assert files == ["/tmp/v.mp4"]

    def test_write_concat_list(self):
        from providers.ffmpeg_video_renderer import _write_concat_list
        out = tempfile.mkdtemp()
        path = _write_concat_list(["/tmp/a.mp4", "/tmp/b.mp4"], out)
        assert path is not None
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "/tmp/a.mp4" in content
        assert "/tmp/b.mp4" in content
        os.remove(path)

    def test_cleanup_concat_list(self):
        from providers.ffmpeg_video_renderer import _cleanup_concat_list
        fd, path = tempfile.mkstemp()
        os.close(fd)
        assert os.path.isfile(path)
        _cleanup_concat_list(path)
        assert not os.path.isfile(path)

    def test_cleanup_nonexistent(self):
        from providers.ffmpeg_video_renderer import _cleanup_concat_list
        _cleanup_concat_list("/nonexistent/file.txt")

    def test_truncate_error(self):
        from providers.ffmpeg_video_renderer import _truncate_error
        assert _truncate_error("") == "unknown error"
        assert _truncate_error("short") == "short"
        long = "x" * 1000
        result = _truncate_error(long, max_len=100)
        assert len(result) < 150

    def test_get_file_size(self):
        from providers.ffmpeg_video_renderer import _get_file_size
        fd, path = tempfile.mkstemp()
        os.write(fd, b"x" * 100)
        os.close(fd)
        assert _get_file_size(path) == 100
        os.remove(path)

    def test_get_file_size_missing(self):
        from providers.ffmpeg_video_renderer import _get_file_size
        assert _get_file_size("/nonexistent") == 0


# ── Result contract ──────────────────────────────────────────────

class TestFFmpegVideoRendererResultContract:
    @patch("providers.ffmpeg_video_renderer._resolve_ffmpeg_path", return_value="/usr/bin/ffmpeg")
    def test_result_ok_has_required_fields(self, _mock):
        from providers.ffmpeg_video_renderer import FFmpegVideoRenderer
        r = FFmpegVideoRenderer(output_dir=tempfile.mkdtemp())
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""
        with patch("providers.ffmpeg_video_renderer.subprocess.run", return_value=mock_proc):
            with patch("providers.ffmpeg_video_renderer.os.path.isfile", side_effect=lambda p: "render_" in p or "video" in p):
                with patch("providers.ffmpeg_video_renderer.os.path.getsize", return_value=2048):
                    result = r.render(VALID_PLAN)
                    assert result.success
                    assert "path" in result.data
                    assert "format" in result.data
                    assert "provider" in result.data
                    assert "size_bytes" in result.data
                    assert isinstance(result.metadata, dict)
                    assert result.metadata["provider"] == "ffmpeg"
