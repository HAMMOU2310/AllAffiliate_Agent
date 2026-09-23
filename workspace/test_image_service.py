"""Tests for ImageService."""

import unittest

from core.result import Result
from services.image_service import ImageService, ImageGenerator, ImageProcessor


class FakeGenerator:
    """Deterministic fake image generator."""

    def __init__(self, result=None):
        self._result = result or Result.ok(
            data={"image": "fake"},
            message="Generated.",
        )
        self.calls = []

    def generate(self, prompt, parameters=None):
        self.calls.append((prompt, parameters))
        return self._result


class FakeFailingGenerator:
    def generate(self, prompt, parameters=None):
        return Result.fail("Generator failed.")


class FakeExceptionGenerator:
    def generate(self, prompt, parameters=None):
        raise RuntimeError("Boom")


class FakeNonResultGenerator:
    def generate(self, prompt, parameters=None):
        return "not a result"


class FakeProcessor:
    def __init__(self, result=None):
        self._result = result or Result.ok(
            data={"path": "/out.png"},
            message="Done.",
        )
        self.calls = []

    def process(self, source, operation, params=None):
        self.calls.append((source, operation, params))
        return self._result


class FakeFailingProcessor:
    def process(self, source, operation, params=None):
        return Result.fail("Processing failed.")


class FakeExceptionProcessor:
    def process(self, source, operation, params=None):
        raise RuntimeError("Boom")


class FakeNonResultProcessor:
    def process(self, source, operation, params=None):
        return "not a result"


class TestImageServiceConstruction(unittest.TestCase):
    def test_construction_with_no_providers(self):
        service = ImageService()
        self.assertIsNotNone(service)

    def test_construction_with_generator(self):
        service = ImageService(generator=FakeGenerator())
        self.assertIsNotNone(service)

    def test_construction_with_processor(self):
        service = ImageService(processor=FakeProcessor())
        self.assertIsNotNone(service)

    def test_construction_with_both(self):
        service = ImageService(
            generator=FakeGenerator(),
            processor=FakeProcessor(),
        )
        self.assertIsNotNone(service)


class TestImageServiceExecute(unittest.TestCase):
    def test_execute_empty_command(self):
        service = ImageService()
        result = service.execute("")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_execute_none_like_command(self):
        service = ImageService()
        result = service.execute("   ")
        self.assertFalse(result.success)

    def test_execute_unsupported_operation(self):
        service = ImageService()
        result = service.execute("bogus something")
        self.assertFalse(result.success)
        self.assertIn("unsupported", result.message.lower())

    def test_execute_generate_no_provider(self):
        service = ImageService()
        result = service.execute("generate a banner")
        self.assertFalse(result.success)
        self.assertIn("no image generation provider", result.message.lower())

    def test_execute_generate_with_provider(self):
        gen = FakeGenerator()
        service = ImageService(generator=gen)
        result = service.execute("generate a banner")
        self.assertTrue(result.success)
        self.assertEqual(len(gen.calls), 1)
        self.assertEqual(gen.calls[0][0], "a banner")

    def test_execute_resize_no_processor(self):
        service = ImageService()
        result = service.execute("resize /img.png 800 600")
        self.assertFalse(result.success)
        self.assertIn("no image processing provider", result.message.lower())

    def test_execute_resize_with_processor(self):
        proc = FakeProcessor()
        service = ImageService(processor=proc)
        result = service.execute("resize /img.png 800 600")
        self.assertTrue(result.success)
        self.assertEqual(len(proc.calls), 1)
        self.assertEqual(proc.calls[0][0], "/img.png")
        self.assertEqual(proc.calls[0][1], "resize")
        self.assertEqual(proc.calls[0][2]["width"], 800)
        self.assertEqual(proc.calls[0][2]["height"], 600)

    def test_execute_crop_with_processor(self):
        proc = FakeProcessor()
        service = ImageService(processor=proc)
        result = service.execute("crop /img.png 10 20 300 400")
        self.assertTrue(result.success)
        self.assertEqual(proc.calls[0][1], "crop")
        self.assertEqual(proc.calls[0][2]["x"], 10)
        self.assertEqual(proc.calls[0][2]["y"], 20)

    def test_execute_thumbnail_with_processor(self):
        proc = FakeProcessor()
        service = ImageService(processor=proc)
        result = service.execute("thumbnail /img.png 200")
        self.assertTrue(result.success)
        self.assertEqual(proc.calls[0][1], "thumbnail")
        self.assertEqual(proc.calls[0][2]["size"], 200)

    def test_execute_convert_with_processor(self):
        proc = FakeProcessor()
        service = ImageService(processor=proc)
        result = service.execute("convert /img.png webp")
        self.assertTrue(result.success)
        self.assertEqual(proc.calls[0][1], "convert")
        self.assertEqual(proc.calls[0][2]["format"], "webp")

    def test_execute_validate_with_processor(self):
        proc = FakeProcessor()
        service = ImageService(processor=proc)
        result = service.execute("validate /img.png")
        self.assertTrue(result.success)
        self.assertEqual(proc.calls[0][1], "validate")

    def test_execute_metadata_with_processor(self):
        proc = FakeProcessor()
        service = ImageService(processor=proc)
        result = service.execute("metadata /img.png")
        self.assertTrue(result.success)
        self.assertEqual(proc.calls[0][1], "metadata")

    def test_execute_missing_args(self):
        proc = FakeProcessor()
        service = ImageService(processor=proc)
        result = service.execute("resize")
        self.assertFalse(result.success)
        self.assertIn("requires input", result.message.lower())


class TestImageServiceGenerate(unittest.TestCase):
    def test_generate_empty_prompt(self):
        service = ImageService(generator=FakeGenerator())
        result = service.generate("")
        self.assertFalse(result.success)
        self.assertIn("invalid", result.message.lower())

    def test_generate_no_provider(self):
        service = ImageService()
        result = service.generate("prompt")
        self.assertFalse(result.success)

    def test_generate_provider_failure(self):
        service = ImageService(generator=FakeFailingGenerator())
        result = service.generate("prompt")
        self.assertFalse(result.success)

    def test_generate_provider_exception(self):
        service = ImageService(generator=FakeExceptionGenerator())
        result = service.generate("prompt")
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    def test_generate_provider_non_result(self):
        service = ImageService(generator=FakeNonResultGenerator())
        result = service.generate("prompt")
        self.assertFalse(result.success)
        self.assertIn("invalid result", result.message.lower())

    def test_generate_success(self):
        gen = FakeGenerator()
        service = ImageService(generator=gen)
        result = service.generate("a beautiful sunset")
        self.assertTrue(result.success)
        self.assertEqual(gen.calls[0][0], "a beautiful sunset")

    def test_generate_with_parameters(self):
        gen = FakeGenerator()
        service = ImageService(generator=gen)
        result = service.generate("prompt", {"size": "512x512"})
        self.assertTrue(result.success)
        self.assertEqual(gen.calls[0][1], {"size": "512x512"})


class TestImageServiceProcessOperation(unittest.TestCase):
    def test_process_no_processor(self):
        service = ImageService()
        result = service._process_operation("resize", "/img.png 800 600")
        self.assertFalse(result.success)

    def test_process_empty_args(self):
        service = ImageService(processor=FakeProcessor())
        result = service._process_operation("resize", "")
        self.assertFalse(result.success)
        self.assertIn("requires input", result.message.lower())

    def test_process_provider_failure(self):
        service = ImageService(processor=FakeFailingProcessor())
        result = service._process_operation("resize", "/img.png 800 600")
        self.assertFalse(result.success)

    def test_process_provider_exception(self):
        service = ImageService(processor=FakeExceptionProcessor())
        result = service._process_operation("resize", "/img.png 800 600")
        self.assertFalse(result.success)
        self.assertIn("execution failed", result.message.lower())

    def test_process_provider_non_result(self):
        service = ImageService(processor=FakeNonResultProcessor())
        result = service._process_operation("resize", "/img.png 800 600")
        self.assertFalse(result.success)
        self.assertIn("invalid result", result.message.lower())


class TestImageServiceParseProcessArgs(unittest.TestCase):
    def test_parse_resize(self):
        params = ImageService._parse_process_args("resize", "/img.png 800 600")
        self.assertEqual(params["source"], "/img.png")
        self.assertEqual(params["width"], 800)
        self.assertEqual(params["height"], 600)

    def test_parse_crop(self):
        params = ImageService._parse_process_args("crop", "/img.png 10 20 300 400")
        self.assertEqual(params["source"], "/img.png")
        self.assertEqual(params["x"], 10)
        self.assertEqual(params["y"], 20)
        self.assertEqual(params["width"], 300)
        self.assertEqual(params["height"], 400)

    def test_parse_thumbnail(self):
        params = ImageService._parse_process_args("thumbnail", "/img.png 200")
        self.assertEqual(params["source"], "/img.png")
        self.assertEqual(params["size"], 200)

    def test_parse_convert(self):
        params = ImageService._parse_process_args("convert", "/img.png webp")
        self.assertEqual(params["source"], "/img.png")
        self.assertEqual(params["format"], "webp")

    def test_parse_validate(self):
        params = ImageService._parse_process_args("validate", "/img.png")
        self.assertEqual(params["source"], "/img.png")

    def test_parse_metadata(self):
        params = ImageService._parse_process_args("metadata", "/img.png")
        self.assertEqual(params["source"], "/img.png")

    def test_parse_empty(self):
        params = ImageService._parse_process_args("resize", "")
        self.assertEqual(params, {})

    def test_parse_invalid_numbers(self):
        params = ImageService._parse_process_args("resize", "/img.png abc def")
        self.assertEqual(params["source"], "/img.png")
        self.assertNotIn("width", params)


if __name__ == "__main__":
    unittest.main()
