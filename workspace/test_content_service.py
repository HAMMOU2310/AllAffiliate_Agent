import unittest

from core.result import Result
from services.content_service import ContentService


DRAFT = {
    "title": "Useful title",
    "body": "Useful body",
    "claims": ["Explicit claim"],
}


class FakeGenerator:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def generate(self, brief, persona=None, format=None):
        self.calls.append((brief, persona, format))
        if self.error is not None:
            raise self.error
        return self.result


class ContentServiceTests(unittest.TestCase):
    def test_construction_and_missing_generator(self):
        self.assertIsInstance(ContentService(), ContentService)
        result = ContentService().create("brief")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No content generator is registered.")

    def test_success_normalizes_draft(self):
        generator = FakeGenerator(Result.ok(data={**DRAFT, "title": " title "}))
        result = ContentService(generator).create(
            " brief ", persona={"tone": "clear"}, format="article"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["title"], "title")
        self.assertEqual(result.metadata["claim_count"], 1)
        self.assertEqual(generator.calls[0], ("brief", {"tone": "clear"}, "article"))

    def test_invalid_inputs_fail(self):
        service = ContentService(FakeGenerator(Result.ok(data=DRAFT)))
        self.assertFalse(service.create("").success)
        self.assertFalse(service.create("brief", persona=[]).success)
        self.assertFalse(service.create("brief", format=" ").success)

    def test_malformed_draft_and_generator_failure_fail(self):
        malformed = {"title": "title", "body": "body", "claims": [1]}
        result = ContentService(FakeGenerator(Result.ok(data=malformed))).create("brief")
        self.assertFalse(result.success)
        failed = ContentService(FakeGenerator(Result.fail("private detail"))).create("brief")
        self.assertEqual(failed.message, "Content generator failed.")

    def test_exception_is_normalized_and_redacted(self):
        result = ContentService(
            FakeGenerator(error=RuntimeError("private detail"))
        ).create("brief")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Content generator execution failed.")
        self.assertNotIn("private detail", repr(result))


if __name__ == "__main__":
    unittest.main()
