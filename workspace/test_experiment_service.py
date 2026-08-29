import unittest
from services.experiment_service import ExperimentService


class ExperimentServiceTests(unittest.TestCase):
    def test_lifecycle(self):
        service = ExperimentService()
        created = service.create("asset", "retention improves", "change hook")
        self.assertTrue(created.success)
        ident = created.data["id"]
        self.assertTrue(service.record_measurement(ident, {"retention": 0.4}).success)
        completed = service.complete(ident, "improved", "keep change")
        self.assertEqual(completed.data["state"], "RESULT")
        self.assertEqual(service.get(ident).data["hypothesis"], "retention improves")

    def test_invalid_and_missing_paths(self):
        service = ExperimentService()
        self.assertFalse(service.create("", "h", "a").success)
        self.assertFalse(service.record_measurement("missing", {"x": 1}).success)
        created = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.record_measurement(created, {"x": float("nan")}).success)
        self.assertFalse(service.complete(created, "").success)


if __name__ == "__main__":
    unittest.main()
