import unittest

from services.media_pipeline_service import MediaPipelineService


class MediaPipelineServiceTests(unittest.TestCase):
    def test_valid_manifest_preserves_video_and_audio(self):
        video = {"timeline": [{"id": "stage"}]}
        audio = {"tracks": [{"id": "voice"}]}
        result = MediaPipelineService().compose(video, audio)
        self.assertTrue(result.success)
        self.assertEqual(result.data["status"], "VALIDATED")
        self.assertEqual(result.data["video_plan"], video)
        self.assertEqual(result.data["audio_plan"], audio)

    def test_invalid_and_empty_plans_fail(self):
        service = MediaPipelineService()
        self.assertFalse(service.compose({}, {}).success)
        self.assertFalse(service.compose({"timeline": []}, {"tracks": [1]}).success)
        self.assertFalse(service.compose({"timeline": [1]}, {"tracks": []}).success)


if __name__ == "__main__":
    unittest.main()
