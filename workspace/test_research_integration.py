"""Integration tests for OpenSERPSearchProvider with local OpenSERP OSS server."""

from __future__ import annotations

import unittest

import pytest

from core.result import Result
from providers.openserp_search_provider import OpenSERPSearchProvider
from services.research_service import ResearchService

_OPENSERP_BASE_URL = "http://127.0.0.1:7000"


def _skip_if_openserp_not_running():
    import requests
    try:
        resp = requests.get(f"{_OPENSERP_BASE_URL}/mega/engines", timeout=3)
        if resp.status_code != 200:
            pytest.skip("OpenSERP local server is not running on http://127.0.0.1:7000")
    except Exception:
        pytest.skip("OpenSERP local server is not running on http://127.0.0.1:7000")


@pytest.mark.integration
class OpenSERPIntegrationTests(unittest.TestCase):
    def test_real_openserp_search(self):
        _skip_if_openserp_not_running()

        provider = OpenSERPSearchProvider(base_url=_OPENSERP_BASE_URL)
        result = provider.search("artificial intelligence trends 2026")

        self.assertIsInstance(result, Result)
        self.assertTrue(result.success, f"Search failed: {result.message}")
        self.assertIsInstance(result.data, list)
        if result.data:
            first = result.data[0]
            self.assertIn("source", first)
            self.assertIn("title", first)
            self.assertIn("content", first)
            self.assertEqual(first["kind"], "FACT")
            self.assertTrue(first["source"].startswith("http"))

    def test_research_service_with_openserp_provider(self):
        _skip_if_openserp_not_running()

        provider = OpenSERPSearchProvider(base_url=_OPENSERP_BASE_URL)
        service = ResearchService([provider])
        result = service.research("best affiliate marketing tools")

        self.assertIsInstance(result, Result)
        self.assertTrue(result.success, f"Research failed: {result.message}")
        self.assertIsInstance(result.data, list)
        self.assertGreater(result.metadata.get("source_count", 0), 0)
        self.assertGreater(result.metadata.get("evidence_count", 0), 0)


if __name__ == "__main__":
    unittest.main()
