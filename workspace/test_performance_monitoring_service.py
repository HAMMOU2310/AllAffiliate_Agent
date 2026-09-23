import unittest

from services.performance_monitoring_service import PerformanceMonitoringService


class PerformanceMonitoringServiceTests(unittest.TestCase):
    def test_isolated_state_and_recording(self):
        first = PerformanceMonitoringService()
        second = PerformanceMonitoringService()
        result = first.record("asset-1", {"views": 10, "clicks": 2})
        self.assertTrue(result.success)
        self.assertEqual(result.data["asset_id"], "asset-1")
        self.assertEqual(second.list_observations().data, [])

    def test_listing_and_filtering(self):
        service = PerformanceMonitoringService()
        service.record("a", {"views": 1})
        service.record("b", {"views": 2})
        self.assertEqual(len(service.list_observations().data), 2)
        self.assertEqual(len(service.list_observations("a").data), 1)

    def test_invalid_metrics_fail(self):
        service = PerformanceMonitoringService()
        self.assertFalse(service.record("", {"views": 1}).success)
        self.assertFalse(service.record("a", {}).success)
        self.assertFalse(service.record("a", {"views": "many"}).success)
        self.assertFalse(service.record("a", {"views": float("nan")}).success)
        self.assertFalse(service.list_observations("").success)


class PerformanceMonitoringServiceEdgeCaseTests(unittest.TestCase):
    def test_record_with_bool_value_fails(self):
        result = PerformanceMonitoringService().record("a", {"flag": True})
        self.assertFalse(result.success)

    def test_record_with_inf_value_fails(self):
        result = PerformanceMonitoringService().record("a", {"val": float("inf")})
        self.assertFalse(result.success)

    def test_record_with_non_string_key_fails(self):
        result = PerformanceMonitoringService().record("a", {123: 1})
        self.assertFalse(result.success)

    def test_record_with_empty_key_fails(self):
        result = PerformanceMonitoringService().record("a", {"": 1})
        self.assertFalse(result.success)

    def test_record_with_non_dict_metrics_fails(self):
        result = PerformanceMonitoringService().record("a", "not_dict")
        self.assertFalse(result.success)

    def test_record_with_non_string_asset_id_fails(self):
        result = PerformanceMonitoringService().record(123, {"views": 1})
        self.assertFalse(result.success)

    def test_list_observations_none_returns_all(self):
        service = PerformanceMonitoringService()
        service.record("a", {"views": 1})
        service.record("b", {"views": 2})
        result = service.list_observations()
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)

    def test_list_observations_filters_correctly(self):
        service = PerformanceMonitoringService()
        service.record("a", {"views": 1})
        service.record("a", {"views": 2})
        service.record("b", {"views": 3})
        result = service.list_observations("a")
        self.assertEqual(len(result.data), 2)
        self.assertTrue(all(o["asset_id"] == "a" for o in result.data))

    def test_list_observations_empty_for_unknown(self):
        service = PerformanceMonitoringService()
        service.record("a", {"views": 1})
        result = service.list_observations("nonexistent")
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 0)

    def test_list_observations_metadata_count(self):
        service = PerformanceMonitoringService()
        service.record("a", {"views": 1})
        result = service.list_observations("a")
        self.assertEqual(result.metadata["count"], 1)
        self.assertEqual(result.metadata["asset_id"], "a")

    def test_list_observations_metadata_none_asset_id(self):
        service = PerformanceMonitoringService()
        service.record("a", {"views": 1})
        result = service.list_observations()
        self.assertIsNone(result.metadata["asset_id"])

    def test_metric_values_are_float(self):
        result = PerformanceMonitoringService().record("a", {"int_val": 5})
        self.assertTrue(result.success)
        self.assertEqual(result.data["metrics"]["int_val"], 5.0)

    def test_metric_keys_are_stripped(self):
        result = PerformanceMonitoringService().record("a", {"  views  ": 1})
        self.assertTrue(result.success)
        self.assertIn("views", result.data["metrics"])

    def test_observation_has_timestamp(self):
        result = PerformanceMonitoringService().record("a", {"views": 1})
        self.assertIn("T", result.data["timestamp"])

    def test_observation_has_id(self):
        result = PerformanceMonitoringService().record("a", {"views": 1})
        self.assertTrue(result.data["id"].startswith("observation-"))

    def test_observation_id_increments(self):
        service = PerformanceMonitoringService()
        r1 = service.record("a", {"views": 1})
        r2 = service.record("a", {"views": 2})
        self.assertNotEqual(r1.data["id"], r2.data["id"])

    def test_observation_metadata_contains_observation_id(self):
        result = PerformanceMonitoringService().record("a", {"views": 1})
        self.assertEqual(result.metadata["observation_id"], result.data["id"])

    def test_record_returns_copy(self):
        service = PerformanceMonitoringService()
        r1 = service.record("a", {"views": 1})
        r2 = service.record("a", {"views": 2})
        self.assertNotEqual(r1.data["metrics"], r2.data["metrics"])

    def test_list_observations_returns_copies(self):
        service = PerformanceMonitoringService()
        service.record("a", {"views": 1})
        r1 = service.list_observations("a")
        r2 = service.list_observations("a")
        self.assertEqual(r1.data, r2.data)
        self.assertIsNot(r1.data, r2.data)


if __name__ == "__main__":
    unittest.main()
