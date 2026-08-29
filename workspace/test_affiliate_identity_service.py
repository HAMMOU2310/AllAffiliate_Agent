import unittest

from services.affiliate_identity_service import AffiliateIdentityService


class AffiliateIdentityServiceTests(unittest.TestCase):
    def test_create_and_get_reusable_identity(self):
        service = AffiliateIdentityService()
        result = service.create(
            "network", "account", "campaign", {"source": "video"}
        )
        self.assertTrue(result.success)
        identity_id = result.data["id"]
        self.assertEqual(service.get(identity_id).data["campaign"], "campaign")
        self.assertEqual(service.get(identity_id).data["parameters"]["source"], "video")

    def test_optional_values_are_supported(self):
        result = AffiliateIdentityService().create("network", "account")
        self.assertTrue(result.success)
        self.assertIsNone(result.data["campaign"])

    def test_invalid_fields_and_secret_parameters_fail(self):
        service = AffiliateIdentityService()
        self.assertFalse(service.create("", "account").success)
        self.assertFalse(service.create("network", "").success)
        self.assertFalse(
            service.create("network", "account", parameters={"api_key": "secret"}).success
        )
        self.assertFalse(service.get("missing").success)


if __name__ == "__main__":
    unittest.main()
