"""Tests for LocalImageProvider."""

import os
import tempfile
import unittest

from PIL import Image

from providers.local_image_provider import LocalImageProvider


def _create_test_image(path, size=(100, 80), color=(255, 0, 0), fmt="PNG"):
    """Create a test image file."""
    img = Image.new("RGB", size, color)
    if fmt.upper() == "JPEG":
        img.save(path, format="JPEG")
    else:
        img.save(path, format=fmt)
    return path


class TestLocalImageProviderConstruction(unittest.TestCase):
    def test_construction(self):
        provider = LocalImageProvider()
        self.assertIsNotNone(provider)


class TestLocalImageProviderResize(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(self.image_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_resize_valid(self):
        result = self.provider.process(self.image_path, "resize", {"width": 50, "height": 40})
        self.assertTrue(result.success)
        self.assertIn("path", result.data)
        self.assertEqual(result.data["width"], 50)
        self.assertEqual(result.data["height"], 40)
        self.assertTrue(os.path.isfile(result.data["path"]))

    def test_resize_invalid_width(self):
        result = self.provider.process(self.image_path, "resize", {"width": -1, "height": 40})
        self.assertFalse(result.success)
        self.assertIn("width", result.message.lower())

    def test_resize_invalid_height(self):
        result = self.provider.process(self.image_path, "resize", {"width": 50, "height": 0})
        self.assertFalse(result.success)
        self.assertIn("height", result.message.lower())

    def test_resize_missing_params(self):
        result = self.provider.process(self.image_path, "resize", None)
        self.assertFalse(result.success)

    def test_resize_empty_params(self):
        result = self.provider.process(self.image_path, "resize", {})
        self.assertFalse(result.success)


class TestLocalImageProviderCrop(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(self.image_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_crop_valid(self):
        result = self.provider.process(self.image_path, "crop", {
            "x": 10, "y": 10, "width": 30, "height": 20,
        })
        self.assertTrue(result.success)
        self.assertEqual(result.data["width"], 30)
        self.assertEqual(result.data["height"], 20)
        self.assertTrue(os.path.isfile(result.data["path"]))

    def test_crop_invalid_x(self):
        result = self.provider.process(self.image_path, "crop", {
            "x": -1, "y": 10, "width": 30, "height": 20,
        })
        self.assertFalse(result.success)

    def test_crop_invalid_dimensions(self):
        result = self.provider.process(self.image_path, "crop", {
            "x": 0, "y": 0, "width": 0, "height": 20,
        })
        self.assertFalse(result.success)

    def test_crop_missing_params(self):
        result = self.provider.process(self.image_path, "crop", None)
        self.assertFalse(result.success)


class TestLocalImageProviderThumbnail(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(self.image_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_thumbnail_valid(self):
        result = self.provider.process(self.image_path, "thumbnail", {"size": 50})
        self.assertTrue(result.success)
        self.assertEqual(result.data["size"], 50)
        self.assertTrue(os.path.isfile(result.data["path"]))

    def test_thumbnail_invalid_size(self):
        result = self.provider.process(self.image_path, "thumbnail", {"size": -1})
        self.assertFalse(result.success)

    def test_thumbnail_missing_params(self):
        result = self.provider.process(self.image_path, "thumbnail", None)
        self.assertFalse(result.success)


class TestLocalImageProviderConvert(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(self.image_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_convert_to_jpeg(self):
        result = self.provider.process(self.image_path, "convert", {"format": "jpeg"})
        self.assertTrue(result.success)
        self.assertEqual(result.data["format"], "JPEG")
        self.assertTrue(os.path.isfile(result.data["path"]))

    def test_convert_to_webp(self):
        result = self.provider.process(self.image_path, "convert", {"format": "webp"})
        self.assertTrue(result.success)
        self.assertEqual(result.data["format"], "WEBP")

    def test_convert_invalid_format(self):
        result = self.provider.process(self.image_path, "convert", {"format": "xyz"})
        self.assertFalse(result.success)
        self.assertIn("unsupported", result.message.lower())

    def test_convert_missing_params(self):
        result = self.provider.process(self.image_path, "convert", None)
        self.assertFalse(result.success)


class TestLocalImageProviderValidate(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(self.image_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_validate_valid(self):
        result = self.provider.process(self.image_path, "validate", None)
        self.assertTrue(result.success)
        self.assertTrue(result.data["valid"])
        self.assertEqual(result.data["width"], 100)
        self.assertEqual(result.data["height"], 80)

    def test_validate_missing_file(self):
        result = self.provider.process("/nonexistent/image.png", "validate", None)
        self.assertTrue(result.success)
        self.assertFalse(result.data["valid"])


class TestLocalImageProviderMetadata(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(self.image_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_metadata_valid(self):
        result = self.provider.process(self.image_path, "metadata", None)
        self.assertTrue(result.success)
        self.assertEqual(result.data["width"], 100)
        self.assertEqual(result.data["height"], 80)
        self.assertEqual(result.data["format"], "PNG")
        self.assertIn("mode", result.data)


class TestLocalImageProviderEdgeCases(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_missing_file(self):
        result = self.provider.process("/nonexistent/img.png", "resize", {"width": 50, "height": 50})
        self.assertFalse(result.success)

    def test_invalid_source(self):
        result = self.provider.process("", "resize", {"width": 50, "height": 50})
        self.assertFalse(result.success)

    def test_unsupported_operation(self):
        path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(path)
        result = self.provider.process(path, "rotate", {"angle": 90})
        self.assertFalse(result.success)

    def test_invalid_operation_type(self):
        path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(path)
        result = self.provider.process(path, 123, None)
        self.assertFalse(result.success)

    def test_invalid_source_type(self):
        result = self.provider.process(123, "resize", {"width": 50, "height": 50})
        self.assertFalse(result.success)

    def test_small_image_resize(self):
        path = os.path.join(self.tmpdir, "tiny.png")
        _create_test_image(path, size=(1, 1))
        result = self.provider.process(path, "resize", {"width": 1, "height": 1})
        self.assertTrue(result.success)

    def test_large_resize(self):
        path = os.path.join(self.tmpdir, "small.png")
        _create_test_image(path, size=(10, 10))
        result = self.provider.process(path, "resize", {"width": 1000, "height": 1000})
        self.assertTrue(result.success)


class TestLocalImageProviderSupportedFormats(unittest.TestCase):
    def setUp(self):
        self.provider = LocalImageProvider()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_convert_jpg(self):
        path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(path)
        result = self.provider.process(path, "convert", {"format": "jpg"})
        self.assertTrue(result.success)

    def test_convert_bmp(self):
        path = os.path.join(self.tmpdir, "test.png")
        _create_test_image(path)
        result = self.provider.process(path, "convert", {"format": "bmp"})
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
