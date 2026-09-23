"""Unit tests for GeminiVideoProvider — all mocked, no network calls."""

from __future__ import annotations

import os
import tempfile
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from core.result import Result


# ── helpers ──────────────────────────────────────────────────────

def _make_operation(
    *,
    done: bool = True,
    video_bytes: bytes | None = b"\x00\x00\x00\x1cftyp",
    mime_type: str = "video/mp4",
    uri: str | None = None,
    error: Any = None,
) -> MagicMock:
    op = MagicMock()
    op.done = done
    op.error = error

    video = MagicMock()
    video.video_bytes = video_bytes
    video.mime_type = mime_type
    video.uri = uri

    generated = MagicMock()
    generated.video = video

    response = MagicMock()
    response.generated_videos = [generated]

    op.response = response
    op.result = None
    op.name = "operations/test-123"
    op.metadata = {}
    return op


def _make_polling_operation(
    total_polls: int = 2,
    video_bytes: bytes = b"\x00\x00\x00\x1cftyp",
) -> MagicMock:
    """Returns an operation object whose done flag flips after N polls."""
    state = {"polls": 0, "total": total_polls}

    def _get_side_effect(op: MagicMock) -> MagicMock:
        state["polls"] += 1
        if state["polls"] >= state["total"]:
            op.done = True
        return op

    op = MagicMock()
    op.done = False
    op.error = None
    op.name = "operations/test-poll"

    video = MagicMock()
    video.video_bytes = video_bytes
    video.mime_type = "video/mp4"
    video.uri = None
    generated = MagicMock()
    video_obj = video
    generated.video = video_obj
    response = MagicMock()
    response.generated_videos = [generated]
    op.response = response
    op.result = None

    return op, _get_side_effect


# ── construction ─────────────────────────────────────────────────

class TestGeminiVideoProviderConstruction:
    def test_construction_default(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        assert p._client is None
        assert p._output_dir is None

    def test_construction_custom_output_dir(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir="/tmp/out")
        assert p._output_dir == "/tmp/out"


# ── prompt validation ────────────────────────────────────────────

class TestGeminiVideoProviderPromptValidation:
    def test_empty_string_prompt(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        r = p.generate("", None)
        assert not r.success
        assert "invalid" in r.message.lower()

    def test_none_prompt(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        r = p.generate(None, None)  # type: ignore
        assert not r.success

    def test_whitespace_only_prompt(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        r = p.generate("   ", None)
        assert not r.success

    def test_int_prompt(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        r = p.generate(123, None)  # type: ignore
        assert not r.success


# ── parameter validation ─────────────────────────────────────────

class TestGeminiVideoProviderParameterValidation:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="k")
    def test_invalid_parameters(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        r = p.generate("test prompt", "not a dict")  # type: ignore
        assert not r.success
        assert "invalid" in r.message.lower()


# ── credentials ──────────────────────────────────────────────────

class TestGeminiVideoProviderCredentials:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value=None)
    def test_missing_credentials(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        r = p.generate("a cinematic video")
        assert not r.success
        assert "credential" in r.message.lower()

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    def test_invalid_sdk_client(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        with patch("providers.gemini_video_provider._create_client", side_effect=RuntimeError("SDK error")):
            p = GeminiVideoProvider()
            r = p.generate("a cinematic video")
            assert not r.success


# ── generation request ───────────────────────────────────────────

class TestGeminiVideoProviderGenerationRequest:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    def test_generation_request_failure(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        client = MagicMock()
        client.models.generate_videos.side_effect = Exception("SDK error")
        p._client = client
        r = p.generate("a cinematic video")
        assert not r.success
        assert "request failed" in r.message.lower()

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    def test_generation_sdk_unavailable(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        with patch("providers.gemini_video_provider._create_client", side_effect=RuntimeError("SDK error")):
            r = p.generate("a cinematic video")
            assert not r.success


# ── successful generation ────────────────────────────────────────

class TestGeminiVideoProviderSuccess:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_generate_success(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = _make_operation(done=True, video_bytes=b"\x00\x00\x00\x1cftyp")
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        r = p.generate("a cinematic ocean sunset")
        assert r.success
        assert r.data["provider"] == "gemini"
        assert r.data["format"] == "mp4"
        assert os.path.exists(r.data["path"])
        assert r.data["size_bytes"] > 0

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_generate_with_parameters(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = _make_operation(done=True)
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        params = {
            "duration_seconds": 5,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "fps": 30,
            "negative_prompt": "no watermarks",
            "enhance_prompt": True,
        }
        r = p.generate("a serene mountain", params)
        assert r.success
        assert r.data["format"] == "mp4"

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_generate_custom_model(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = _make_operation(done=True)
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        r = p.generate("test", {"model": "veo-custom"})
        assert r.success
        call_kwargs = client.models.generate_videos.call_args
        assert call_kwargs.kwargs["model"] == "veo-custom"

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_generate_metadata_contains_provider(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = _make_operation(done=True)
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        r = p.generate("metadata test")
        assert r.success
        assert r.metadata["provider"] == "gemini"
        assert r.metadata["model"] == "veo-2.0-generate-001"
        assert r.metadata["prompt"] == "metadata test"


# ── polling ──────────────────────────────────────────────────────

class TestGeminiVideoProviderPolling:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_polling_completes(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op, side_effect = _make_polling_operation(total_polls=2)
        client.models.generate_videos.return_value = op
        client.operations.get.side_effect = side_effect
        p._client = client
        r = p.generate("a busy street")
        assert r.success

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._MAX_POLL_ATTEMPTS", 3)
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_polling_timeout(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = MagicMock()
        op.done = False
        op.error = None
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        r = p.generate("a busy street")
        assert not r.success
        assert "timed out" in r.message.lower()

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_polling_exception_returns_none(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = MagicMock()
        op.done = False
        client.models.generate_videos.return_value = op
        client.operations.get.side_effect = Exception("network error")
        p._client = client
        r = p.generate("test poll exception")
        assert not r.success

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_polling_sleep_exception(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = MagicMock()
        op.done = False
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        with patch("providers.gemini_video_provider.time.sleep", side_effect=Exception("interrupt")):
            r = p.generate("test sleep exception")
            assert not r.success


# ── response extraction ──────────────────────────────────────────

class TestGeminiVideoProviderResponseExtraction:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_no_generated_videos(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        client = MagicMock()
        op = MagicMock()
        op.done = True
        op.error = None
        resp = MagicMock()
        resp.generated_videos = []
        op.response = resp
        client.models.generate_videos.return_value = op
        p._client = client
        r = p.generate("test no videos")
        assert not r.success
        assert "no generated video" in r.message.lower()

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_none_response(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        client = MagicMock()
        op = MagicMock()
        op.done = True
        op.error = None
        op.response = None
        op.result = None
        client.models.generate_videos.return_value = op
        p._client = client
        r = p.generate("test none response")
        assert not r.success

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_empty_video_bytes(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        client = MagicMock()
        op = _make_operation(done=True, video_bytes=b"", mime_type="video/mp4")
        client.models.generate_videos.return_value = op
        p._client = client
        r = p.generate("test empty video bytes")
        assert not r.success

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_none_video_object(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        client = MagicMock()
        op = MagicMock()
        op.done = True
        op.error = None
        generated = MagicMock()
        generated.video = None
        resp = MagicMock()
        resp.generated_videos = [generated]
        op.response = resp
        client.models.generate_videos.return_value = op
        p._client = client
        r = p.generate("test none video object")
        assert not r.success

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_no_response_or_result(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        client = MagicMock()
        op = MagicMock()
        op.done = True
        op.error = None
        op.response = None
        op.result = None
        client.models.generate_videos.return_value = op
        p._client = client
        r = p.generate("test no response or result")
        assert not r.success


# ── file saving ──────────────────────────────────────────────────

class TestGeminiVideoProviderFileSaving:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_save_exception(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=None)
        client = MagicMock()
        op = _make_operation(done=True)
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        with patch("builtins.open", side_effect=PermissionError("denied")):
            r = p.generate("test save exception")
            assert not r.success
            assert "save" in r.message.lower()

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_video_file_saved_correctly(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        import shutil
        out = tempfile.mkdtemp()
        try:
            p = GeminiVideoProvider(output_dir=out)
            client = MagicMock()
            op = _make_operation(done=True, video_bytes=b"\x00fake-mp4-data")
            client.models.generate_videos.return_value = op
            client.operations.get.return_value = op
            p._client = client
            r = p.generate("file save test")
            assert r.success
            assert os.path.exists(r.data["path"])
            with open(r.data["path"], "rb") as f:
                assert f.read() == b"\x00fake-mp4-data"
        finally:
            shutil.rmtree(out, ignore_errors=True)

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_output_dir_created_if_missing(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        base = tempfile.mkdtemp()
        nested = os.path.join(base, "a", "b", "c")
        try:
            p = GeminiVideoProvider(output_dir=nested)
            client = MagicMock()
            op = _make_operation(done=True, video_bytes=b"\x00data")
            client.models.generate_videos.return_value = op
            client.operations.get.return_value = op
            p._client = client
            r = p.generate("nested dir test")
            assert r.success
            assert os.path.isdir(nested)
        finally:
            import shutil
            shutil.rmtree(base, ignore_errors=True)


# ── remote failure ───────────────────────────────────────────────

class TestGeminiVideoProviderRemoteFailure:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_operation_error(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        client = MagicMock()
        op = _make_operation(done=True, error={"message": "SAFETY"})
        client.models.generate_videos.return_value = op
        p._client = client
        r = p.generate("test operation error")
        assert not r.success
        assert "failed remotely" in r.message.lower()


# ── protocol conformance ─────────────────────────────────────────

class TestGeminiVideoProviderProtocolConformance:
    def test_has_generate_method(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        assert callable(getattr(p, "generate", None))

    def test_generate_signature(self):
        import inspect
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider()
        sig = inspect.signature(p.generate)
        params = list(sig.parameters.keys())
        assert "prompt" in params
        assert "parameters" in params

    def test_return_type(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        from services.video_production_service import VideoGenerator
        assert hasattr(GeminiVideoProvider, "generate")

    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_conforms_to_video_generator(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        from services.video_production_service import VideoGenerator
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = _make_operation(done=True)
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        r = p.generate("protocol test")
        assert isinstance(r, Result)


# ── config building ──────────────────────────────────────────────

class TestGeminiVideoProviderConfigBuilding:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_config_built_from_valid_params(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = _make_operation(done=True)
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        r = p.generate("config test", {"duration_seconds": 5, "fps": 30, "seed": 42})
        assert r.success

    def test_config_none_when_empty(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        r = GeminiVideoProvider._build_config({})
        assert r is None

    def test_config_none_when_no_dict(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        r = GeminiVideoProvider._build_config(None)  # type: ignore
        assert r is None

    def test_config_ignores_unknown_keys(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        r = GeminiVideoProvider._build_config({"unknown_key": "value"})
        assert r is None

    def test_config_ignores_wrong_types(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        r = GeminiVideoProvider._build_config({"duration_seconds": "not_int"})
        assert r is None

    def test_config_all_valid_fields(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        r = GeminiVideoProvider._build_config({
            "duration_seconds": 5,
            "fps": 30,
            "seed": 42,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "negative_prompt": "no blur",
            "enhance_prompt": True,
            "generate_audio": True,
            "number_of_videos": 1,
            "person_generation": "allow_adult",
        })
        assert r is not None


# ── mime conversion ──────────────────────────────────────────────

class TestGeminiVideoProviderMimeConversion:
    def test_mp4(self):
        from providers.gemini_video_provider import _mime_to_format
        assert _mime_to_format("video/mp4") == "mp4"

    def test_webm(self):
        from providers.gemini_video_provider import _mime_to_format
        assert _mime_to_format("video/webm") == "webm"

    def test_unknown_falls_back(self):
        from providers.gemini_video_provider import _mime_to_format
        assert _mime_to_format("video/unknown") == "mp4"

    def test_case_insensitive(self):
        from providers.gemini_video_provider import _mime_to_format
        assert _mime_to_format("Video/MP4") == "mp4"


# ── extract_video edge cases ────────────────────────────────────

class TestGeminiVideoProviderExtractVideo:
    def test_extract_with_result_field(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        op = MagicMock()
        op.done = True
        op.error = None
        op.response = None

        video = MagicMock()
        video.video_bytes = b"\x00data"
        video.mime_type = "video/webm"
        video.uri = None
        generated = MagicMock()
        generated.video = video
        resp = MagicMock()
        resp.generated_videos = [generated]
        op.result = resp

        r = GeminiVideoProvider._extract_video(op)
        assert r is not None
        assert r[1] == "video/webm"

    def test_extract_uri_only(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        op = MagicMock()
        video = MagicMock()
        video.video_bytes = None
        video.mime_type = "video/mp4"
        video.uri = "gs://bucket/video.mp4"
        generated = MagicMock()
        generated.video = video
        resp = MagicMock()
        resp.generated_videos = [generated]
        op.response = resp
        op.result = None

        r = GeminiVideoProvider._extract_video(op)
        assert r is not None
        assert r[2] == "gs://bucket/video.mp4"

    def test_extract_exception(self):
        from providers.gemini_video_provider import GeminiVideoProvider
        op = MagicMock()
        op.response = "not a real object"
        op.result = None
        r = GeminiVideoProvider._extract_video(op)
        assert r is None


# ── Result contract ──────────────────────────────────────────────

class TestGeminiVideoProviderResultContract:
    @patch("providers.gemini_video_provider._resolve_api_key", return_value="valid-key")
    @patch("providers.gemini_video_provider._POLL_INTERVAL_SECONDS", 0)
    def test_result_ok_has_required_fields(self, _mock_key):
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        client = MagicMock()
        op = _make_operation(done=True)
        client.models.generate_videos.return_value = op
        client.operations.get.return_value = op
        p._client = client
        r = p.generate("contract test")
        assert r.success
        assert "path" in r.data
        assert "format" in r.data
        assert "provider" in r.data
        assert "size_bytes" in r.data
        assert "mime_type" in r.data
        assert isinstance(r.metadata, dict)
        assert r.metadata["provider"] == "gemini"


# ── integration ──────────────────────────────────────────────────

class TestGeminiVideoProviderIntegration:
    @pytest.mark.integration
    def test_real_gemini_video_generation(self):
        key = os.getenv("GEMINI_API_KEY")
        if not key or not key.strip():
            pytest.skip("GEMINI_API_KEY not set")
        from providers.gemini_video_provider import GeminiVideoProvider
        p = GeminiVideoProvider(output_dir=tempfile.mkdtemp())
        r = p.generate(
            "A single red autumn leaf falling slowly in soft natural light",
            {"duration_seconds": 5},
        )
        assert isinstance(r, Result)
        if r.success:
            assert "path" in r.data
            assert r.data["provider"] == "gemini"
        else:
            assert "failed" in r.message.lower() or "timed out" in r.message.lower()
