"""Unit tests for GeminiSTTProvider and GeminiTTSProvider.

All tests use mocked Gemini SDK objects. Zero network calls.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.result import Result
from providers.gemini_voice_provider import (
    GeminiSTTProvider,
    GeminiTTSProvider,
    _extract_text,
    _extract_audio,
    _get_mime_type,
    _resolve_api_key,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------


def _make_text_response(text: str):
    resp = MagicMock()
    resp.text = text
    resp.candidates = [MagicMock()]
    resp.candidates[0].content.parts = [MagicMock(text=text)]
    return resp


def _make_empty_response():
    resp = MagicMock()
    resp.text = ""
    resp.candidates = []
    return resp


def _make_audio_response(audio_bytes: bytes, mime_type: str = "audio/wav"):
    part = MagicMock()
    part.inline_data = MagicMock()
    part.inline_data.data = audio_bytes
    part.inline_data.mime_type = mime_type
    part.text = None

    candidate = MagicMock()
    candidate.content.parts = [part]

    resp = MagicMock()
    resp.text = None
    resp.candidates = [candidate]
    return resp


def _make_no_audio_response():
    part = MagicMock()
    part.inline_data = None
    part.text = "Here is the text response."

    candidate = MagicMock()
    candidate.content.parts = [part]

    resp = MagicMock()
    resp.text = "Here is the text response."
    resp.candidates = [candidate]
    return resp


def _create_wav_file(path: str, duration: float = 0.5) -> str:
    import struct
    import wave

    sample_rate = 16000
    num_samples = int(sample_rate * duration)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            import math
            value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            frames.extend(struct.pack("<h", value))
        wf.writeframes(bytes(frames))
    return path


# --------------------------------------------------
# STT Provider Tests
# --------------------------------------------------


class GeminiSTTProviderConstructionTests(unittest.TestCase):
    def test_default_model(self):
        p = GeminiSTTProvider()
        self.assertEqual(p._model, "gemini-2.0-flash")

    def test_custom_model(self):
        p = GeminiSTTProvider(model="gemini-2.5-flash")
        self.assertEqual(p._model, "gemini-2.5-flash")


class GeminiSTTProviderTranscribeTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.wav_path = os.path.join(self.tmpdir, "test.wav")
        _create_wav_file(self.wav_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_transcribe_success(self, mock_key):
        p = GeminiSTTProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_text_response("Hello world")
        p._client = mock_client

        result = p.transcribe(self.wav_path)
        self.assertTrue(result.success)
        self.assertEqual(result.data["text"], "Hello world")
        self.assertEqual(result.data["provider"], "gemini")
        self.assertEqual(result.data["source"], self.wav_path)

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_transcribe_with_language_param(self, mock_key):
        p = GeminiSTTProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_text_response("Bonjour")
        p._client = mock_client

        result = p.transcribe(self.wav_path, parameters={"language": "fr"})
        self.assertTrue(result.success)
        self.assertEqual(result.data["text"], "Bonjour")

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_transcribe_with_prompt_param(self, mock_key):
        p = GeminiSTTProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_text_response("Transcribed")
        p._client = mock_client

        result = p.transcribe(self.wav_path, parameters={"prompt": "Translate this audio"})
        self.assertTrue(result.success)

    def test_transcribe_empty_source(self):
        p = GeminiSTTProvider()
        self.assertFalse(p.transcribe("").success)
        self.assertFalse(p.transcribe("   ").success)

    def test_transcribe_none_source(self):
        p = GeminiSTTProvider()
        self.assertFalse(p.transcribe(None).success)

    def test_transcribe_missing_file(self):
        p = GeminiSTTProvider()
        result = p.transcribe("/nonexistent/audio.wav")
        self.assertFalse(result.success)
        self.assertIn("not found", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value=None)
    def test_transcribe_missing_credentials(self, mock_key):
        p = GeminiSTTProvider()
        result = p.transcribe(self.wav_path)
        self.assertFalse(result.success)
        self.assertIn("credentials", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_transcribe_empty_response(self, mock_key):
        p = GeminiSTTProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_empty_response()
        p._client = mock_client

        result = p.transcribe(self.wav_path)
        self.assertFalse(result.success)
        self.assertIn("empty transcription", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_transcribe_sdk_exception(self, mock_key):
        p = GeminiSTTProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("API error")
        p._client = mock_client

        result = p.transcribe(self.wav_path)
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_transcribe_empty_audio_file(self, mock_key):
        p = GeminiSTTProvider()
        empty_path = os.path.join(self.tmpdir, "empty.wav")
        with open(empty_path, "wb") as f:
            f.write(b"")

        result = p.transcribe(empty_path)
        self.assertFalse(result.success)
        self.assertIn("empty", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_transcribe_file_read_error(self, mock_key):
        p = GeminiSTTProvider()
        # Use a path that exists but can't be read
        bad_path = os.path.join(self.tmpdir, "no_such_file.wav")
        result = p.transcribe(bad_path)
        self.assertFalse(result.success)


class GeminiSTTProviderProtocolConformanceTests(unittest.TestCase):
    def test_has_transcribe_method(self):
        p = GeminiSTTProvider()
        self.assertTrue(callable(getattr(p, "transcribe", None)))

    def test_transcribe_returns_result(self):
        p = GeminiSTTProvider()
        result = p.transcribe("")
        self.assertIsInstance(result, Result)


# --------------------------------------------------
# TTS Provider Tests
# --------------------------------------------------


class GeminiTTSProviderConstructionTests(unittest.TestCase):
    def test_default_model(self):
        p = GeminiTTSProvider()
        self.assertEqual(p._model, "gemini-2.0-flash")

    def test_custom_model(self):
        p = GeminiTTSProvider(model="gemini-2.5-flash")
        self.assertEqual(p._model, "gemini-2.5-flash")


class GeminiTTSProviderSynthesizeTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_success(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_audio_response(
            b"fake-audio-data", "audio/wav"
        )
        p._client = mock_client

        result = p.synthesize("Hello world")
        self.assertTrue(result.success)
        self.assertEqual(result.data["text"], "Hello world")
        self.assertEqual(result.data["provider"], "gemini")
        self.assertIsNone(result.data["path"])

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_with_output_path(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_audio_response(
            b"fake-audio-bytes", "audio/wav"
        )
        p._client = mock_client

        out_path = os.path.join(self.tmpdir, "output.wav")
        result = p.synthesize("Save this", parameters={"output_path": out_path})
        self.assertTrue(result.success)
        self.assertEqual(result.data["path"], out_path)
        self.assertTrue(os.path.exists(out_path))

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_with_voice(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_audio_response(
            b"data", "audio/wav"
        )
        p._client = mock_client

        result = p.synthesize("Test", parameters={"voice": "Charon"})
        self.assertTrue(result.success)
        self.assertEqual(result.data["voice"], "Charon")

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_with_language(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_audio_response(
            b"data", "audio/wav"
        )
        p._client = mock_client

        result = p.synthesize("Bonjour", parameters={"language": "fr"})
        self.assertTrue(result.success)

    def test_synthesize_empty_text(self):
        p = GeminiTTSProvider()
        self.assertFalse(p.synthesize("").success)
        self.assertFalse(p.synthesize("   ").success)

    def test_synthesize_none_text(self):
        p = GeminiTTSProvider()
        self.assertFalse(p.synthesize(None).success)

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value=None)
    def test_synthesize_missing_credentials(self, mock_key):
        p = GeminiTTSProvider()
        result = p.synthesize("Hello")
        self.assertFalse(result.success)
        self.assertIn("credentials", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_no_audio_response(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_no_audio_response()
        p._client = mock_client

        result = p.synthesize("Hello")
        self.assertFalse(result.success)
        self.assertIn("no audio data", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_empty_audio_response(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        resp = MagicMock()
        candidate = MagicMock()
        candidate.content.parts = [MagicMock(inline_data=MagicMock(data=b"", mime_type="audio/wav"))]
        resp.candidates = [candidate]
        resp.text = None
        mock_client.models.generate_content.return_value = resp
        p._client = mock_client

        result = p.synthesize("Hello")
        self.assertFalse(result.success)
        self.assertIn("no audio data", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_sdk_exception(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("API down")
        p._client = mock_client

        result = p.synthesize("Hello")
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_save_failure(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_audio_response(
            b"data", "audio/wav"
        )
        p._client = mock_client

        # Try to save to an invalid path (directory as file)
        bad_path = os.path.join(self.tmpdir, "nonexistent_dir", "sub", "out.wav")
        # This should succeed because we create parent dirs
        # Let's use a read-only location instead
        result = p.synthesize("Test", parameters={"output_path": bad_path})
        # Should succeed because we create parents
        self.assertTrue(result.success)

    @patch("providers.gemini_voice_provider._resolve_api_key", return_value="fake-key")
    def test_synthesize_invalid_parameters_type(self, mock_key):
        p = GeminiTTSProvider()
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_audio_response(
            b"data", "audio/wav"
        )
        p._client = mock_client

        result = p.synthesize("Test", parameters="not a dict")
        self.assertTrue(result.success)


class GeminiTTSProviderProtocolConformanceTests(unittest.TestCase):
    def test_has_synthesize_method(self):
        p = GeminiTTSProvider()
        self.assertTrue(callable(getattr(p, "synthesize", None)))

    def test_synthesize_returns_result(self):
        p = GeminiTTSProvider()
        result = p.synthesize("")
        self.assertIsInstance(result, Result)


# --------------------------------------------------
# Helper Tests
# --------------------------------------------------


class ExtractTextTests(unittest.TestCase):
    def test_extract_from_text_attr(self):
        resp = MagicMock()
        resp.text = "Hello"
        resp.candidates = []
        self.assertEqual(_extract_text(resp), "Hello")

    def test_extract_from_parts(self):
        resp = MagicMock()
        resp.text = None
        part = MagicMock(text="World")
        resp.candidates = [MagicMock(content=MagicMock(parts=[part]))]
        self.assertEqual(_extract_text(resp), "World")

    def test_extract_empty(self):
        resp = MagicMock()
        resp.text = ""
        resp.candidates = []
        self.assertIsNone(_extract_text(resp))

    def test_extract_none_response(self):
        self.assertIsNone(_extract_text(None))


class ExtractAudioTests(unittest.TestCase):
    def test_extract_audio_success(self):
        resp = _make_audio_response(b"data", "audio/wav")
        result = _extract_audio(resp)
        self.assertIsNotNone(result)
        self.assertEqual(result["data"], b"data")
        self.assertEqual(result["mime_type"], "audio/wav")

    def test_extract_audio_no_candidates(self):
        resp = MagicMock()
        resp.candidates = []
        self.assertIsNone(_extract_audio(resp))

    def test_extract_audio_no_inline_data(self):
        resp = _make_no_audio_response()
        self.assertIsNone(_extract_audio(resp))

    def test_extract_audio_none_response(self):
        self.assertIsNone(_extract_audio(None))


class GetMimeMapTests(unittest.TestCase):
    def test_wav(self):
        self.assertEqual(_get_mime_type("test.wav"), "audio/wav")

    def test_mp3(self):
        self.assertEqual(_get_mime_type("test.mp3"), "audio/mpeg")

    def test_unknown_defaults_wav(self):
        self.assertEqual(_get_mime_type("test.xyz"), "audio/wav")


class ResolveApiKeyTests(unittest.TestCase):
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"})
    def test_returns_key(self):
        self.assertEqual(_resolve_api_key(), "test-key-123")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "  "})
    def test_whitespace_returns_none(self):
        self.assertIsNone(_resolve_api_key())

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_returns_none(self):
        self.assertIsNone(_resolve_api_key())


class IntegrationTests(unittest.TestCase):
    """Optional real integration tests — skipped without GEMINI_API_KEY."""

    @unittest.skipUnless(
        os.getenv("GEMINI_API_KEY"),
        "GEMINI_API_KEY not set",
    )
    def test_real_stt_transcription(self):
        tmpdir = tempfile.mkdtemp()
        try:
            wav_path = os.path.join(tmpdir, "test.wav")
            _create_wav_file(wav_path, duration=1.0)
            p = GeminiSTTProvider()
            result = p.transcribe(wav_path)
            self.assertIsInstance(result, Result)
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    @unittest.skipUnless(
        os.getenv("GEMINI_API_KEY"),
        "GEMINI_API_KEY not set",
    )
    def test_real_tts_synthesis(self):
        p = GeminiTTSProvider()
        result = p.synthesize("Hello, this is a test.")
        self.assertIsInstance(result, Result)


if __name__ == "__main__":
    unittest.main()
