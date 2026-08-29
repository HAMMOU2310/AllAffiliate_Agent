import unittest

from services.persona_service import PersonaService


class PersonaServiceTests(unittest.TestCase):
    def test_valid_reusable_profile(self):
        persona = {
            "audience": "builders",
            "language": "en",
            "tone": "clear",
            "prohibited_claims": ["guaranteed results"],
            "platform_constraints": {"length": "short"},
        }
        result = PersonaService().validate(persona)
        self.assertTrue(result.success)
        self.assertEqual(result.data["audience"], "builders")
        self.assertEqual(result.data["prohibited_claims"], ["guaranteed results"])

    def test_missing_and_invalid_fields_fail(self):
        service = PersonaService()
        self.assertFalse(service.validate({}).success)
        self.assertFalse(
            service.validate({"audience": "a", "language": "en", "tone": ""}).success
        )
        self.assertFalse(
            service.validate(
                {"audience": "a", "language": "en", "tone": "clear", "unknown": True}
            ).success
        )

    def test_optional_field_types_are_checked(self):
        result = PersonaService().validate(
            {"audience": "a", "language": "en", "tone": "clear", "cta_behavior": 3}
        )
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()
