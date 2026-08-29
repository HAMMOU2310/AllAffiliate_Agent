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


if __name__ == "__main__":
    unittest.main()
