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


class ContentServiceEdgeCaseTests(unittest.TestCase):
    def test_generator_without_generate_method(self):
        class BadGenerator:
            pass

        result = ContentService(BadGenerator()).create("brief")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Content generator is invalid.")

    def test_empty_claims_list(self):
        draft = {"title": "Title", "body": "Body", "claims": []}
        generator = FakeGenerator(Result.ok(data=draft))
        result = ContentService(generator).create("brief")
        self.assertTrue(result.success)
        self.assertEqual(result.data["claims"], [])
        self.assertEqual(result.metadata["claim_count"], 0)

    def test_persona_none_is_valid(self):
        generator = FakeGenerator(Result.ok(data=DRAFT))
        result = ContentService(generator).create("brief", persona=None)
        self.assertTrue(result.success)
        self.assertIsNone(generator.calls[0][1])

    def test_format_none_is_valid(self):
        generator = FakeGenerator(Result.ok(data=DRAFT))
        result = ContentService(generator).create("brief", format=None)
        self.assertTrue(result.success)
        self.assertIsNone(generator.calls[0][2])

    def test_normalize_draft_non_mapping(self):
        result = ContentService._normalize_draft("bad")
        self.assertIsNone(result)

    def test_normalize_draft_missing_title(self):
        result = ContentService._normalize_draft(
            {"body": "b", "claims": ["c"]}
        )
        self.assertIsNone(result)

    def test_normalize_draft_empty_title(self):
        result = ContentService._normalize_draft(
            {"title": "  ", "body": "b", "claims": ["c"]}
        )
        self.assertIsNone(result)

    def test_normalize_draft_missing_body(self):
        result = ContentService._normalize_draft(
            {"title": "t", "claims": ["c"]}
        )
        self.assertIsNone(result)

    def test_normalize_draft_empty_body(self):
        result = ContentService._normalize_draft(
            {"title": "t", "body": "  ", "claims": ["c"]}
        )
        self.assertIsNone(result)

    def test_normalize_draft_missing_claims(self):
        result = ContentService._normalize_draft(
            {"title": "t", "body": "b"}
        )
        self.assertIsNone(result)

    def test_normalize_draft_non_list_claims(self):
        result = ContentService._normalize_draft(
            {"title": "t", "body": "b", "claims": "not a list"}
        )
        self.assertIsNone(result)

    def test_normalize_draft_non_string_claim(self):
        result = ContentService._normalize_draft(
            {"title": "t", "body": "b", "claims": [123]}
        )
        self.assertIsNone(result)

    def test_normalize_draft_empty_string_claim(self):
        result = ContentService._normalize_draft(
            {"title": "t", "body": "b", "claims": ["  "]}
        )
        self.assertIsNone(result)

    def test_generator_exception_returns_fail(self):
        generator = FakeGenerator(error=RuntimeError("crash"))
        result = ContentService(generator).create("brief")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Content generator execution failed.")

    def test_generator_returns_non_result(self):
        class NonResultGenerator:
            def generate(self, brief, persona=None, format=None):
                return "not a result"

        result = ContentService(NonResultGenerator()).create("brief")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Content generator failed.")

    def test_format_stripped_in_metadata(self):
        generator = FakeGenerator(Result.ok(data=DRAFT))
        result = ContentService(generator).create("brief", format="  article  ")
        self.assertTrue(result.success)
        self.assertEqual(result.metadata["format"], "article")

    def test_extra_fields_preserved(self):
        draft = {**DRAFT, "extra_field": "preserved"}
        generator = FakeGenerator(Result.ok(data=draft))
        result = ContentService(generator).create("brief")
        self.assertTrue(result.success)
        self.assertEqual(result.data["extra_field"], "preserved")

    def test_title_and_body_stripped(self):
        draft = {"title": "  Title  ", "body": "  Body  ", "claims": ["claim"]}
        generator = FakeGenerator(Result.ok(data=draft))
        result = ContentService(generator).create("brief")
        self.assertTrue(result.success)
        self.assertEqual(result.data["title"], "Title")
        self.assertEqual(result.data["body"], "Body")


if __name__ == "__main__":
    unittest.main()
