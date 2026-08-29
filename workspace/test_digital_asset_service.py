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


if __name__ == "__main__":
    unittest.main()
