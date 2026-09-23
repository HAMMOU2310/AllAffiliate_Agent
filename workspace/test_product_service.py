import unittest

from services.product_service import ProductService


class ProductServiceTests(unittest.TestCase):
    def test_multi_signal_ranking_and_provenance(self):
        result = ProductService().rank(
            [
                {"id": "b", "name": "B", "signals": {"sales": 5, "quality": 7}},
                {"id": "a", "name": "A", "signals": {"sales": 8, "quality": 8}},
            ]
        )
        self.assertTrue(result.success)
        self.assertEqual([item["id"] for item in result.data], ["a", "b"])
        self.assertEqual(result.data[0]["score"], 8.0)
        self.assertEqual(result.data[0]["signals_used"], ["sales", "quality"])

    def test_empty_candidates_are_valid(self):
        result = ProductService().rank([])
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])

    def test_invalid_candidates_fail(self):
        service = ProductService()
        self.assertFalse(service.rank("invalid").success)
        self.assertFalse(service.rank([{"id": "x"}]).success)
        self.assertFalse(
            service.rank([{"id": "x", "name": "X", "signals": {"sales": 1}}]).success
        )
        self.assertFalse(
            service.rank(
                [
                    {"id": "x", "name": "X", "signals": {"a": 1, "b": 2}},
                    {"id": "x", "name": "Again", "signals": {"a": 2, "b": 3}},
                ]
            ).success
        )

    def test_non_numeric_signal_fails(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"a": 1, "b": "unknown"}}]
        )
        self.assertFalse(result.success)


class ProductServiceEdgeCaseTests(unittest.TestCase):
    def test_bool_signal_value_fails(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"a": True, "b": 2}}]
        )
        self.assertFalse(result.success)

    def test_inf_signal_value_fails(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"a": float("inf"), "b": 2}}]
        )
        self.assertFalse(result.success)

    def test_nan_signal_value_fails(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"a": float("nan"), "b": 2}}]
        )
        self.assertFalse(result.success)

    def test_empty_signal_key_fails(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"": 1, "b": 2}}]
        )
        self.assertFalse(result.success)

    def test_non_mapping_candidate_fails(self):
        result = ProductService().rank(["not_a_dict"])
        self.assertFalse(result.success)

    def test_candidate_without_id_fails(self):
        result = ProductService().rank([{"name": "X", "signals": {"a": 1, "b": 2}}])
        self.assertFalse(result.success)

    def test_candidate_without_name_fails(self):
        result = ProductService().rank([{"id": "x", "signals": {"a": 1, "b": 2}}])
        self.assertFalse(result.success)

    def test_candidate_without_signals_fails(self):
        result = ProductService().rank([{"id": "x", "name": "X"}])
        self.assertFalse(result.success)

    def test_single_signal_fails(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"a": 1}}]
        )
        self.assertFalse(result.success)

    def test_score_is_arithmetic_mean(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"a": 2, "b": 4, "c": 6}}]
        )
        self.assertTrue(result.success)
        self.assertAlmostEqual(result.data[0]["score"], 4.0)

    def test_sorting_by_score_descending(self):
        result = ProductService().rank([
            {"id": "low", "name": "Low", "signals": {"a": 1, "b": 2}},
            {"id": "high", "name": "High", "signals": {"a": 9, "b": 8}},
            {"id": "mid", "name": "Mid", "signals": {"a": 5, "b": 5}},
        ])
        self.assertEqual([x["id"] for x in result.data], ["high", "mid", "low"])

    def test_sorting_tiebreak_by_id(self):
        result = ProductService().rank([
            {"id": "b", "name": "B", "signals": {"a": 5, "b": 5}},
            {"id": "a", "name": "A", "signals": {"a": 5, "b": 5}},
        ])
        self.assertEqual([x["id"] for x in result.data], ["a", "b"])

    def test_duplicate_ids_fail(self):
        result = ProductService().rank([
            {"id": "x", "name": "A", "signals": {"a": 1, "b": 2}},
            {"id": "x", "name": "B", "signals": {"a": 3, "b": 4}},
        ])
        self.assertFalse(result.success)
        self.assertIn("unique", result.message.lower())

    def test_id_stripped_in_output(self):
        result = ProductService().rank(
            [{"id": "  x  ", "name": "X", "signals": {"a": 1, "b": 2}}]
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["id"], "x")

    def test_name_stripped_in_output(self):
        result = ProductService().rank(
            [{"id": "x", "name": "  X  ", "signals": {"a": 1, "b": 2}}]
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data[0]["name"], "X")

    def test_signals_used_listed(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"sales": 5, "quality": 7}}]
        )
        self.assertEqual(result.data[0]["signals_used"], ["sales", "quality"])

    def test_metadata_contains_ranking_method(self):
        result = ProductService().rank(
            [{"id": "x", "name": "X", "signals": {"a": 1, "b": 2}}]
        )
        self.assertIn("ranking_method", result.metadata)
        self.assertEqual(result.metadata["candidate_count"], 1)

    def test_empty_candidates_return_empty(self):
        result = ProductService().rank([])
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])

    def test_non_sequence_input_fails(self):
        self.assertFalse(ProductService().rank("invalid").success)
        self.assertFalse(ProductService().rank(123).success)


if __name__ == "__main__":
    unittest.main()
