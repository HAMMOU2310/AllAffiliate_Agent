import os
import tempfile
import unittest

from core.result import Result
from providers.audio_utils import (
    create_wav_file,
    create_wav_bytes,
    validate_wav_file,
    extract_wav_metadata,
)


class FakeSTTProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.last_source = None
        self.last_params = None

    def transcribe(self, source, parameters=None):
        self.last_source = source
        self.last_params = parameters
        if self.error is not None:
            raise self.error
        return self.result


class FakeTTSProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.last_text = None
        self.last_params = None

    def synthesize(self, text, parameters=None):
        self.last_text = text
        self.last_params = parameters
        if self.error is not None:
            raise self.error
        return self.result


class FakeInterpreter:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def interpret(self, instruction):
        if self.error is not None:
            raise self.error
        return self.result


PLAN = {
    "tracks": [
        {
            "id": "narration",
            "start": 0,
            "duration": 3,
            "kind": "voice",
            "continuity": {"previous": None},
        }
    ]
}


class AudioServiceConstructionTests(unittest.TestCase):
    def test_default_construction(self):
        from services.audio_service import AudioService
        svc = AudioService()
        self.assertIsInstance(svc, AudioService)

    def test_construction_with_providers(self):
        from services.audio_service import AudioService
        stt = FakeSTTProvider()
        tts = FakeTTSProvider()
        interp = FakeInterpreter()
        svc = AudioService(interpreter=interp, stt_provider=stt, tts_provider=tts)
        self.assertIsInstance(svc, AudioService)


class AudioServiceTranscribeTests(unittest.TestCase):
    def test_transcribe_success(self):
        from services.audio_service import AudioService
        provider = FakeSTTProvider(
            result=Result.ok(
                data={"text": "hello world", "language": "en"},
                message="Transcription complete.",
            )
        )
        svc = AudioService(stt_provider=provider)
        result = svc.transcribe("test.wav")
        self.assertTrue(result.success)
        self.assertEqual(result.data["text"], "hello world")
        self.assertEqual(provider.last_source, "test.wav")

    def test_transcribe_with_parameters(self):
        from services.audio_service import AudioService
        provider = FakeSTTProvider(
            result=Result.ok(data={"text": "hi"})
        )
        svc = AudioService(stt_provider=provider)
        params = {"language": "fr"}
        result = svc.transcribe("audio.wav", parameters=params)
        self.assertTrue(result.success)
        self.assertEqual(provider.last_params, params)

    def test_transcribe_empty_source(self):
        from services.audio_service import AudioService
        svc = AudioService(stt_provider=FakeSTTProvider())
        self.assertFalse(svc.transcribe("").success)
        self.assertFalse(svc.transcribe("   ").success)
        self.assertFalse(svc.transcribe(None).success)

    def test_transcribe_no_provider(self):
        from services.audio_service import AudioService
        svc = AudioService()
        result = svc.transcribe("test.wav")
        self.assertFalse(result.success)
        self.assertIn("speech-to-text provider", result.message.lower())

    def test_transcribe_invalid_provider(self):
        from services.audio_service import AudioService
        svc = AudioService(stt_provider="not_a_provider")
        result = svc.transcribe("test.wav")
        self.assertFalse(result.success)

    def test_transcribe_provider_failure(self):
        from services.audio_service import AudioService
        provider = FakeSTTProvider(result=Result.fail("model error"))
        svc = AudioService(stt_provider=provider)
        result = svc.transcribe("test.wav")
        self.assertFalse(result.success)

    def test_transcribe_provider_exception(self):
        from services.audio_service import AudioService
        provider = FakeSTTProvider(error=RuntimeError("api down"))
        svc = AudioService(stt_provider=provider)
        result = svc.transcribe("test.wav")
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    def test_transcribe_invalid_result_type(self):
        from services.audio_service import AudioService
        provider = FakeSTTProvider(result="not_a_result")
        svc = AudioService(stt_provider=provider)
        result = svc.transcribe("test.wav")
        self.assertFalse(result.success)


class AudioServiceSpeakTests(unittest.TestCase):
    def test_speak_success(self):
        from services.audio_service import AudioService
        provider = FakeTTSProvider(
            result=Result.ok(
                data={"path": "/tmp/out.wav", "format": "wav", "duration": 2.0},
                message="Speech synthesized.",
            )
        )
        svc = AudioService(tts_provider=provider)
        result = svc.speak("Hello world")
        self.assertTrue(result.success)
        self.assertEqual(provider.last_text, "Hello world")

    def test_speak_with_parameters(self):
        from services.audio_service import AudioService
        provider = FakeTTSProvider(
            result=Result.ok(data={"path": "/tmp/out.wav"})
        )
        svc = AudioService(tts_provider=provider)
        params = {"voice": "alloy"}
        result = svc.speak("Test", parameters=params)
        self.assertTrue(result.success)
        self.assertEqual(provider.last_params, params)

    def test_speak_empty_text(self):
        from services.audio_service import AudioService
        svc = AudioService(tts_provider=FakeTTSProvider())
        self.assertFalse(svc.speak("").success)
        self.assertFalse(svc.speak("   ").success)
        self.assertFalse(svc.speak(None).success)

    def test_speak_no_provider(self):
        from services.audio_service import AudioService
        svc = AudioService()
        result = svc.speak("Hello")
        self.assertFalse(result.success)
        self.assertIn("text-to-speech provider", result.message.lower())

    def test_speak_invalid_provider(self):
        from services.audio_service import AudioService
        svc = AudioService(tts_provider="not_a_provider")
        result = svc.speak("Hello")
        self.assertFalse(result.success)

    def test_speak_provider_failure(self):
        from services.audio_service import AudioService
        provider = FakeTTSProvider(result=Result.fail("quota exceeded"))
        svc = AudioService(tts_provider=provider)
        result = svc.speak("Hello")
        self.assertFalse(result.success)

    def test_speak_provider_exception(self):
        from services.audio_service import AudioService
        provider = FakeTTSProvider(error=RuntimeError("network error"))
        svc = AudioService(tts_provider=provider)
        result = svc.speak("Hello")
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    def test_speak_invalid_result_type(self):
        from services.audio_service import AudioService
        provider = FakeTTSProvider(result={"not": "a result"})
        svc = AudioService(tts_provider=provider)
        result = svc.speak("Hello")
        self.assertFalse(result.success)


class AudioServiceExecuteTests(unittest.TestCase):
    def test_execute_transcribe(self):
        from services.audio_service import AudioService
        provider = FakeSTTProvider(
            result=Result.ok(data={"text": "transcribed"})
        )
        svc = AudioService(stt_provider=provider)
        result = svc.execute("transcribe audio.wav")
        self.assertTrue(result.success)

    def test_execute_speak(self):
        from services.audio_service import AudioService
        provider = FakeTTSProvider(
            result=Result.ok(data={"path": "/tmp/out.wav"})
        )
        svc = AudioService(tts_provider=provider)
        result = svc.execute("speak Hello world")
        self.assertTrue(result.success)

    def test_execute_create_plan(self):
        from services.audio_service import AudioService
        interp = FakeInterpreter(Result.ok(data=PLAN))
        svc = AudioService(interpreter=interp)
        result = svc.execute("create_plan voice narration")
        self.assertTrue(result.success)

    def test_execute_unsupported_operation(self):
        from services.audio_service import AudioService
        svc = AudioService()
        result = svc.execute("volume up")
        self.assertFalse(result.success)
        self.assertIn("Unsupported audio operation", result.message)

    def test_execute_empty_command(self):
        from services.audio_service import AudioService
        svc = AudioService()
        self.assertFalse(svc.execute("").success)
        self.assertFalse(svc.execute(None).success)


class AudioServiceCreatePlanTests(unittest.TestCase):
    def test_construction_and_missing_interpreter(self):
        from services.audio_service import AudioService
        self.assertIsInstance(AudioService(), AudioService)
        self.assertFalse(AudioService().create_plan("voice").success)

    def test_success_normalizes_tracks(self):
        from services.audio_service import AudioService
        result = AudioService(FakeInterpreter(Result.ok(data=PLAN))).create_plan(" voice ")
        self.assertTrue(result.success)
        self.assertEqual(result.data["tracks"][0]["start"], 0.0)

    def test_invalid_and_duplicate_tracks_fail(self):
        from services.audio_service import AudioService
        malformed = {"tracks": [{"id": "x", "start": 0, "duration": 1, "kind": "voice"}]}
        duplicate = {"tracks": [
            {"id": "x", "start": 0, "duration": 1, "kind": "voice", "continuity": {}},
            {"id": "x", "start": 1, "duration": 1, "kind": "voice", "continuity": {}},
        ]}
        self.assertFalse(AudioService(FakeInterpreter(Result.ok(data=malformed))).create_plan("x").success)
        self.assertFalse(AudioService(FakeInterpreter(Result.ok(data=duplicate))).create_plan("x").success)

    def test_failure_and_exception_are_normalized(self):
        from services.audio_service import AudioService
        failed = AudioService(FakeInterpreter(Result.fail("private"))).create_plan("x")
        errored = AudioService(FakeInterpreter(error=RuntimeError("private"))).create_plan("x")
        self.assertEqual(failed.message, "Audio interpreter failed.")
        self.assertEqual(errored.message, "Audio interpreter execution failed.")


class WavFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_create_wav_file(self):
        path = os.path.join(self.tmpdir, "test.wav")
        result = create_wav_file(path, duration_seconds=0.5)
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(result.data["format"], "wav")
        self.assertEqual(result.data["sample_rate"], 16000)
        self.assertEqual(result.data["channels"], 1)

    def test_create_wav_custom_params(self):
        path = os.path.join(self.tmpdir, "custom.wav")
        result = create_wav_file(
            path,
            sample_rate=44100,
            duration_seconds=2.0,
            channels=2,
            sample_width=2,
            frequency=1000.0,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["sample_rate"], 44100)
        self.assertEqual(result.data["channels"], 2)

    def test_validate_wav_valid(self):
        path = os.path.join(self.tmpdir, "valid.wav")
        create_wav_file(path, duration_seconds=0.5)
        result = validate_wav_file(path)
        self.assertTrue(result.success)
        self.assertTrue(result.data["valid"])
        self.assertGreater(result.data["duration_seconds"], 0)

    def test_validate_wav_missing(self):
        result = validate_wav_file("/nonexistent/file.wav")
        self.assertFalse(result.success)

    def test_validate_wav_invalid_content(self):
        path = os.path.join(self.tmpdir, "invalid.wav")
        with open(path, "wb") as f:
            f.write(b"not a wav file")
        result = validate_wav_file(path)
        self.assertFalse(result.success)

    def test_create_wav_bytes(self):
        result = create_wav_bytes(duration_seconds=0.5)
        self.assertTrue(result.success)
        self.assertIn("bytes", result.data)
        self.assertGreater(result.data["size_bytes"], 0)
        self.assertEqual(result.data["format"], "wav")

    def test_extract_wav_metadata(self):
        path = os.path.join(self.tmpdir, "meta.wav")
        create_wav_file(path, sample_rate=22050, duration_seconds=1.0)
        meta = extract_wav_metadata(path)
        self.assertEqual(meta["sample_rate"], 22050)
        self.assertEqual(meta["format"], "wav")
        self.assertIn("duration_seconds", meta)

    def test_extract_wav_metadata_missing(self):
        meta = extract_wav_metadata("/nonexistent/file.wav")
        self.assertFalse(meta.get("valid", True))


if __name__ == "__main__":
    unittest.main()
