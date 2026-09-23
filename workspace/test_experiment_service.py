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


class ExperimentServiceEdgeCaseTests(unittest.TestCase):
    def test_get_missing_experiment_fails(self):
        result = ExperimentService().get("nonexistent")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Experiment is not registered.")

    def test_get_with_non_string_id_fails(self):
        result = ExperimentService().get(123)
        self.assertFalse(result.success)

    def test_create_strips_whitespace(self):
        service = ExperimentService()
        result = service.create("  asset  ", "  hypothesis  ", "  action  ")
        self.assertTrue(result.success)
        self.assertEqual(result.data["asset_id"], "asset")
        self.assertEqual(result.data["hypothesis"], "hypothesis")
        self.assertEqual(result.data["action"], "action")

    def test_create_with_empty_after_strip_fails(self):
        service = ExperimentService()
        self.assertFalse(service.create("  ", "h", "a").success)
        self.assertFalse(service.create("a", "  ", "a").success)
        self.assertFalse(service.create("a", "h", "  ").success)

    def test_create_with_non_string_fails(self):
        service = ExperimentService()
        self.assertFalse(service.create(123, "h", "a").success)
        self.assertFalse(service.create("a", None, "a").success)

    def test_id_auto_increment(self):
        service = ExperimentService()
        r1 = service.create("a", "h1", "a1")
        r2 = service.create("a", "h2", "a2")
        self.assertEqual(int(r1.data["id"].split("-")[1]) + 1,
                         int(r2.data["id"].split("-")[1]))

    def test_record_measurement_with_bool_value_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.record_measurement(cid, {"flag": True}).success)

    def test_record_measurement_with_inf_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.record_measurement(cid, {"val": float("inf")}).success)

    def test_record_measurement_with_non_string_key_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.record_measurement(cid, {123: 1}).success)

    def test_record_measurement_with_empty_key_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.record_measurement(cid, {"": 1}).success)

    def test_record_measurement_with_non_dict_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.record_measurement(cid, "not a dict").success)

    def test_record_measurement_with_empty_dict_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.record_measurement(cid, {}).success)

    def test_record_measurement_with_non_string_experiment_id_fails(self):
        service = ExperimentService()
        self.assertFalse(service.record_measurement(123, {"x": 1}).success)

    def test_multiple_measurements_accumulate(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        service.record_measurement(cid, {"views": 100})
        result = service.record_measurement(cid, {"views": 200})
        self.assertTrue(result.success)
        self.assertEqual(len(result.data["measurements"]), 2)

    def test_measurement_values_are_float(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        result = service.record_measurement(cid, {"int_val": 5, "float_val": 3.14})
        self.assertTrue(result.success)
        self.assertEqual(result.data["measurements"][0]["int_val"], 5.0)
        self.assertEqual(result.data["measurements"][0]["float_val"], 3.14)

    def test_measurement_key_whitespace_stripped(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        result = service.record_measurement(cid, {"  metric  ": 1})
        self.assertTrue(result.success)
        self.assertIn("metric", result.data["measurements"][0])

    def test_complete_with_none_learning(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        result = service.complete(cid, "result")
        self.assertTrue(result.success)
        self.assertIsNone(result.data["learning"])

    def test_complete_with_empty_learning_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.complete(cid, "result", "  ").success)

    def test_complete_with_non_string_result_fails(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertFalse(service.complete(cid, 123).success)

    def test_complete_with_non_string_experiment_id_fails(self):
        service = ExperimentService()
        self.assertFalse(service.complete(123, "result").success)

    def test_complete_result_stripped(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        result = service.complete(cid, "  result  ", "  learning  ")
        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], "result")
        self.assertEqual(result.data["learning"], "learning")

    def test_state_transition_to_result(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        self.assertEqual(service.get(cid).data["state"], "EXPERIMENT")
        service.complete(cid, "done")
        self.assertEqual(service.get(cid).data["state"], "RESULT")

    def test_created_at_is_iso_format(self):
        service = ExperimentService()
        result = service.create("a", "h", "a")
        self.assertIn("T", result.data["created_at"])

    def test_get_returns_copy(self):
        service = ExperimentService()
        cid = service.create("a", "h", "a").data["id"]
        r1 = service.get(cid)
        r2 = service.get(cid)
        self.assertEqual(r1.data, r2.data)
        self.assertIsNot(r1.data, r2.data)


if __name__ == "__main__":
    unittest.main()
