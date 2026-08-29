"""Integration test: ContentService → Gemini real API pipeline.

This test validates the complete provider-neutral content-generation
chain using a real Gemini API call. It does NOT mock any layer.

Chain tested:
  ContentService
    → CloudAIContentGenerator
      → CloudAIService
        → GeminiProvider
          → Google Gemini API

This is NOT a new production component. It uses existing architecture only.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root before checking for keys.
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

import pytest  # noqa: E402

from core.result import Result  # noqa: E402
from services.cloud_ai_service import CloudAIService  # noqa: E402
from providers.gemini_provider import GeminiProvider  # noqa: E402
from providers.cloud_ai_content_generator import CloudAIContentGenerator  # noqa: E402
from services.content_service import ContentService  # noqa: E402


def _gemini_available() -> bool:
    key = os.getenv("GEMINI_API_KEY")
    return bool(key and key.strip())


skip_no_gemini = pytest.mark.skipif(
    not _gemini_available(),
    reason="GEMINI_API_KEY not configured — skipping real pipeline test",
)


def _build_content_service() -> ContentService:
    """Wire the real provider-neutral content pipeline with Gemini."""
    cloud_ai = CloudAIService()
    cloud_ai.register_provider("gemini", GeminiProvider())

    generator = CloudAIContentGenerator(
        cloud_ai_service=cloud_ai,
        model="gemini-2.5-flash-lite",
    )
    return ContentService(generator)


@pytest.mark.integration
@skip_no_gemini
class TestContentGenerationWorkflow:
    """Real end-to-end content generation through the existing pipeline."""

    def test_full_pipeline_returns_validated_draft(self):
        service = _build_content_service()

        result = service.create(
            brief="Write one short sentence about solar energy benefits.",
            format="sentence",
        )

        assert result.success is True
        assert isinstance(result.data, dict)

        draft = result.data
        assert "title" in draft
        assert "body" in draft
        assert "claims" in draft

        assert isinstance(draft["title"], str)
        assert len(draft["title"].strip()) > 0

        assert isinstance(draft["body"], str)
        assert len(draft["body"].strip()) > 0

        assert isinstance(draft["claims"], list)

    def test_pipeline_preserves_provider_neutrality(self):
        service = _build_content_service()

        result = service.create(
            brief="Write a one-line description of wind power.",
            format="description",
        )

        assert result.success is True
        assert isinstance(result.data["title"], str)
        assert isinstance(result.data["body"], str)
        assert isinstance(result.data["claims"], list)

    def test_metadata_contains_format(self):
        service = _build_content_service()

        result = service.create(
            brief="Write a single fact about hydroelectric energy.",
            format="fact",
        )

        assert result.success is True
        assert result.metadata["format"] == "fact"
        assert isinstance(result.metadata["claim_count"], int)


class TestContentServiceValidation:
    """Contract-level validation — no real API call needed. No integration marker."""

    def test_missing_generator_returns_failure(self):
        service = ContentService(generator=None)
        result = service.create("test brief")
        assert result.success is False
        assert result.message == "No content generator is registered."

    def test_invalid_brief_returns_failure(self):
        service = _build_content_service()
        result = service.create("")
        assert result.success is False
        assert result.message == "Content brief is invalid."

    def test_invalid_persona_returns_failure(self):
        service = _build_content_service()
        result = service.create("test brief", persona="not a dict")
        assert result.success is False
        assert result.message == "Content persona is invalid."

    def test_invalid_format_returns_failure(self):
        service = _build_content_service()
        result = service.create("test brief", format=123)
        assert result.success is False
        assert result.message == "Content format is invalid."
