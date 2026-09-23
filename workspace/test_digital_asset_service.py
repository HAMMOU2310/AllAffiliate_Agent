import unittest

from services.digital_asset_service import DigitalAssetService


class DigitalAssetServiceTests(unittest.TestCase):
    def test_construction_is_isolated(self):
        first = DigitalAssetService()
        second = DigitalAssetService()
        self.assertTrue(first.register("website", "One").success)
        self.assertEqual(second.list_assets().data, [])

    def test_register_get_and_list(self):
        service = DigitalAssetService()
        created = service.register("product", " Product ", {"category": "tools"})
        self.assertTrue(created.success)
        asset_id = created.data["id"]
        self.assertEqual(service.get(asset_id).data["name"], "Product")
        self.assertEqual(len(service.list_assets("product").data), 1)

    def test_invalid_values_and_protected_metadata_fail(self):
        service = DigitalAssetService()
        self.assertFalse(service.register("unknown", "name").success)
        self.assertFalse(service.register("website", "").success)
        self.assertFalse(service.register("website", "name", {"api_key": "x"}).success)
        self.assertFalse(service.get("missing").success)
        self.assertFalse(service.list_assets("unknown").success)

    def test_empty_list_is_success(self):
        result = DigitalAssetService().list_assets()
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])


class DigitalAssetServiceEdgeCaseTests(unittest.TestCase):
    def test_register_with_metadata_none(self):
        result = DigitalAssetService().register("website", "site", None)
        self.assertTrue(result.success)
        self.assertEqual(result.data["metadata"], {})

    def test_register_with_non_dict_metadata_fails(self):
        result = DigitalAssetService().register("website", "site", "bad")
        self.assertFalse(result.success)
        self.assertIn("metadata", result.message.lower())

    def test_get_empty_string_fails(self):
        result = DigitalAssetService().get("")
        self.assertFalse(result.success)

    def test_get_whitespace_string_fails(self):
        result = DigitalAssetService().get("   ")
        self.assertFalse(result.success)

    def test_get_non_string_fails(self):
        result = DigitalAssetService().get(123)
        self.assertFalse(result.success)

    def test_list_assets_with_none_returns_all(self):
        service = DigitalAssetService()
        service.register("website", "A")
        service.register("product", "B")
        result = service.list_assets(None)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)

    def test_list_assets_filters_by_type(self):
        service = DigitalAssetService()
        service.register("website", "A")
        service.register("product", "B")
        result = service.list_assets("website")
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["type"], "website")

    def test_list_assets_count_metadata(self):
        service = DigitalAssetService()
        service.register("website", "A")
        result = service.list_assets()
        self.assertEqual(result.metadata["count"], 1)
        self.assertIsNone(result.metadata["type"])

    def test_register_metadata_count(self):
        service = DigitalAssetService()
        result = service.register("website", "A")
        self.assertEqual(result.metadata["count"], 1)
        self.assertEqual(result.metadata["asset_id"], "asset-1")

    def test_all_asset_types_accepted(self):
        service = DigitalAssetService()
        for atype in ["website", "landing_page", "product", "affiliate_link",
                      "video", "channel", "campaign", "social_account", "content_asset"]:
            result = service.register(atype, f"name-{atype}")
            self.assertTrue(result.success, f"Failed for type: {atype}")

    def test_secret_key_variations_blocked(self):
        service = DigitalAssetService()
        for key in ["secret", "token", "password", "api_key", "apikey", "API_KEY", "Secret"]:
            result = service.register("website", "name", {key: "val"})
            self.assertFalse(result.success, f"Should block key: {key}")

    def test_non_string_metadata_keys_ignored_for_secrets(self):
        service = DigitalAssetService()
        result = service.register("website", "name", {123: "val"})
        self.assertTrue(result.success)

    def test_metadata_deep_copy(self):
        service = DigitalAssetService()
        meta = {"key": "val"}
        service.register("website", "name", meta)
        meta["key"] = "changed"
        result = service.get("asset-1")
        self.assertEqual(result.data["metadata"]["key"], "val")

    def test_name_stripped_in_output(self):
        result = DigitalAssetService().register("website", "  padded  ")
        self.assertEqual(result.data["name"], "padded")

    def test_type_lowercased_in_output(self):
        result = DigitalAssetService().register("Website", "name")
        self.assertEqual(result.data["type"], "website")

    def test_asset_id_increments(self):
        service = DigitalAssetService()
        r1 = service.register("website", "A")
        r2 = service.register("website", "B")
        self.assertEqual(int(r1.data["id"].split("-")[1]) + 1,
                         int(r2.data["id"].split("-")[1]))

    def test_get_returns_copy(self):
        service = DigitalAssetService()
        service.register("website", "A")
        r1 = service.get("asset-1")
        r2 = service.get("asset-1")
        self.assertEqual(r1.data, r2.data)
        self.assertIsNot(r1.data, r2.data)

    def test_list_assets_with_non_string_type_fails(self):
        result = DigitalAssetService().list_assets(123)
        self.assertFalse(result.success)

    def test_list_assets_with_unknown_type_fails(self):
        result = DigitalAssetService().list_assets("unknown_type")
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()
