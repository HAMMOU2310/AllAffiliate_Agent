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


if __name__ == "__main__":
    unittest.main()
