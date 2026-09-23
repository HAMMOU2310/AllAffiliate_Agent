"""Tests for GeminiImageProvider."""

import io
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from core.result import Result
from providers.gemini_image_provider import GeminiImageProvider


def _fake_image_bytes(fmt="PNG"):
    """Create minimal valid image bytes."""
    from PIL import Image
    img = Image.new("RGB", (64, 48), (128, 64, 32))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def _fake_response(image_bytes=None, mime_type="image/png"):
    """Create a fake Gemini GenerateImagesResponse."""
    if image_bytes is None:
        image_bytes = _fake_image_bytes()

    image = MagicMock()
    image.image_bytes = image_bytes
    image.mime_type = mime_type

    generated = MagicMock()
    generated.image = image

    response = MagicMock()
    response.generated_images = [generated]
    return response


class TestGeminiImageProviderConstruction(unittest.TestCase):
    def test_construction_default(self):
        provider = GeminiImageProvider()
        self.assertIsNotNone(provider)

    def test_construction_with_output_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            provider = GeminiImageProvider(output_dir=tmpdir)
            self.assertIsNotNone(provider)


class TestGeminiImageProviderGenerateValidation(unittest.TestCase):
    def test_generate_empty_prompt(self):
        provider = GeminiImageProvider()
        result = provider.generate("")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_generate_whitespace_prompt(self):
        provider = GeminiImageProvider()
        result = provider.generate("   ")
        self.assertFalse(result.success)

    def test_generate_none_like_prompt(self):
        provider = GeminiImageProvider()
        result = provider.generate(123)
        self.assertFalse(result.success)

    def test_generate_invalid_parameters(self):
        provider = GeminiImageProvider()
        result = provider.generate("prompt", "not_a_dict")
        self.assertFalse(result.success)

    @patch.dict(os.environ, {}, clear=True)
    def test_generate_missing_credentials(self):
        provider = GeminiImageProvider()
        result = provider.generate("prompt")
        self.assertFalse(result.success)
        self.assertIn("credentials", result.message.lower())


class TestGeminiImageProviderGenerateSuccess(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.provider = GeminiImageProvider(output_dir=self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_success(self):
        fake_client = MagicMock()
        fake_client.models.generate_images.return_value = _fake_response()
        self.provider._client = fake_client

        result = self.provider.generate("a red square")

        self.assertTrue(result.success)
        self.assertIn("path", result.data)
        self.assertEqual(result.data["format"], "PNG")
        self.assertEqual(result.data["width"], 64)
        self.assertEqual(result.data["height"], 48)
        self.assertEqual(result.data["provider"], "gemini")
        self.assertTrue(os.path.isfile(result.data["path"]))

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_with_parameters(self):
        fake_client = MagicMock()
        fake_client.models.generate_images.return_value = _fake_response()
        self.provider._client = fake_client

        result = self.provider.generate("prompt", {"seed": 42, "number_of_images": 1})

        self.assertTrue(result.success)
        fake_client.models.generate_images.assert_called_once()

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_metadata_contains_provider(self):
        fake_client = MagicMock()
        fake_client.models.generate_images.return_value = _fake_response()
        self.provider._client = fake_client

        result = self.provider.generate("test")

        self.assertEqual(result.metadata["provider"], "gemini")
        self.assertIn("model", result.metadata)
        self.assertIn("prompt", result.metadata)


class TestGeminiImageProviderGenerateFailures(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.provider = GeminiImageProvider(output_dir=self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_sdk_exception(self):
        fake_client = MagicMock()
        fake_client.models.generate_images.side_effect = RuntimeError("API error")
        self.provider._client = fake_client

        result = self.provider.generate("prompt")
        self.assertFalse(result.success)
        self.assertIn("failed", result.message.lower())

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_empty_response(self):
        fake_client = MagicMock()
        response = MagicMock()
        response.generated_images = []
        fake_client.models.generate_images.return_value = response
        self.provider._client = fake_client

        result = self.provider.generate("prompt")
        self.assertFalse(result.success)
        self.assertIn("no generated images", result.message.lower())

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_none_response_images(self):
        fake_client = MagicMock()
        response = MagicMock()
        response.generated_images = None
        fake_client.models.generate_images.return_value = response
        self.provider._client = fake_client

        result = self.provider.generate("prompt")
        self.assertFalse(result.success)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_image_object_none(self):
        fake_client = MagicMock()
        generated = MagicMock()
        generated.image = None
        response = MagicMock()
        response.generated_images = [generated]
        fake_client.models.generate_images.return_value = response
        self.provider._client = fake_client

        result = self.provider.generate("prompt")
        self.assertFalse(result.success)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_image_bytes_empty(self):
        fake_client = MagicMock()
        image = MagicMock()
        image.image_bytes = b""
        image.mime_type = "image/png"
        generated = MagicMock()
        generated.image = image
        response = MagicMock()
        response.generated_images = [generated]
        fake_client.models.generate_images.return_value = response
        self.provider._client = fake_client

        result = self.provider.generate("prompt")
        self.assertFalse(result.success)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_image_bytes_none(self):
        fake_client = MagicMock()
        image = MagicMock()
        image.image_bytes = None
        image.mime_type = "image/png"
        generated = MagicMock()
        generated.image = image
        response = MagicMock()
        response.generated_images = [generated]
        fake_client.models.generate_images.return_value = response
        self.provider._client = fake_client

        result = self.provider.generate("prompt")
        self.assertFalse(result.success)


class TestGeminiImageProviderConfigBuilding(unittest.TestCase):
    def test_build_config_none(self):
        config = GeminiImageProvider._build_config(None)
        self.assertIsNone(config)

    def test_build_config_empty(self):
        config = GeminiImageProvider._build_config({})
        self.assertIsNone(config)

    def test_build_config_valid_fields(self):
        config = GeminiImageProvider._build_config({"seed": 42, "number_of_images": 1})
        self.assertIsNotNone(config)

    def test_build_config_invalid_fields_ignored(self):
        config = GeminiImageProvider._build_config({"unknown_field": "value"})
        self.assertIsNone(config)

    def test_build_config_mixed_valid_invalid(self):
        config = GeminiImageProvider._build_config({"seed": 42, "bogus": "value"})
        self.assertIsNotNone(config)


class TestGeminiImageProviderImageExtraction(unittest.TestCase):
    def test_extract_image_success(self):
        response = _fake_response()
        result = GeminiImageProvider._extract_image(response)
        self.assertIsNotNone(result)
        self.assertIsInstance(result[0], bytes)
        self.assertEqual(result[1], "image/png")

    def test_extract_image_empty_list(self):
        response = MagicMock()
        response.generated_images = []
        result = GeminiImageProvider._extract_image(response)
        self.assertIsNone(result)

    def test_extract_image_none_list(self):
        response = MagicMock()
        response.generated_images = None
        result = GeminiImageProvider._extract_image(response)
        self.assertIsNone(result)

    def test_extract_image_none_image_object(self):
        generated = MagicMock()
        generated.image = None
        response = MagicMock()
        response.generated_images = [generated]
        result = GeminiImageProvider._extract_image(response)
        self.assertIsNone(result)

    def test_extract_image_exception(self):
        response = MagicMock()
        response.generated_images = "not a list"
        result = GeminiImageProvider._extract_image(response)
        self.assertIsNone(result)

    def test_extract_image_jpeg_mime(self):
        response = _fake_response(mime_type="image/jpeg")
        result = GeminiImageProvider._extract_image(response)
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "image/jpeg")


class TestGeminiImageProviderJpegOutput(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.provider = GeminiImageProvider(output_dir=self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"})
    def test_generate_jpeg_output(self):
        jpeg_bytes = _fake_image_bytes("JPEG")
        fake_client = MagicMock()
        fake_client.models.generate_images.return_value = _fake_response(
            image_bytes=jpeg_bytes, mime_type="image/jpeg"
        )
        self.provider._client = fake_client

        result = self.provider.generate("prompt")
        self.assertTrue(result.success)
        self.assertEqual(result.data["format"], "JPEG")


class TestGeminiImageProviderProtocolConformance(unittest.TestCase):
    def test_has_generate_method(self):
        provider = GeminiImageProvider()
        self.assertTrue(callable(getattr(provider, "generate", None)))

    def test_generate_returns_result(self):
        provider = GeminiImageProvider()
        result = provider.generate("")
        self.assertIsInstance(result, Result)


if __name__ == "__main__":
    unittest.main()
