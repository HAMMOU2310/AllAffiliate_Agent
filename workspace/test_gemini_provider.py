"""Unit tests for GeminiProvider — provider-neutral CloudAIProvider contract."""

from types import SimpleNamespace

import pytest

from core.result import Result
from providers.gemini_provider import GeminiProvider
from services.cloud_ai_service import CloudAIService


class FakeGeminiModels:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        return self._response


class FakeGeminiClient:
    def __init__(self, models):
        self.models = models


def successful_response(text="generated text"):
    return SimpleNamespace(text=text)


def successful_response_with_candidates(text="generated text"):
    candidate = SimpleNamespace(
        content=SimpleNamespace(
            parts=[SimpleNamespace(text=text)]
        )
    )
    return SimpleNamespace(
        text=None,
        candidates=[candidate],
    )


def empty_response():
    return SimpleNamespace(text=None, candidates=[])


def test_construction():
    provider = GeminiProvider()
    assert callable(provider.generate)
    assert provider._client is None


def test_success_forwards_model_and_parameters(monkeypatch):
    models = FakeGeminiModels(response=successful_response())
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate(
        "hello",
        model="gemini-2.0-flash",
        parameters={"temperature": 0.2},
    )

    assert result.success is True
    assert result.data == "generated text"
    assert result.errors == []
    assert len(models.calls) == 1
    assert models.calls[0]["model"] == "gemini-2.0-flash"
    assert models.calls[0]["contents"] == "hello"
    assert models.calls[0]["config"]["temperature"] == 0.2


def test_success_with_response_from_candidates(monkeypatch):
    models = FakeGeminiModels(response=successful_response_with_candidates("candidate text"))
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate("hello", model="gemini-2.0-flash")

    assert result.success is True
    assert result.data == "candidate text"


def test_default_model_is_used_when_none(monkeypatch):
    models = FakeGeminiModels(response=successful_response())
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate("hello")

    assert result.success is True
    assert models.calls[0]["model"] == "gemini-2.5-flash-lite"


def test_invalid_prompt_empty():
    provider = GeminiProvider()
    result = provider.generate("")
    assert result.success is False
    assert result.message == "Prompt is invalid."


def test_invalid_prompt_whitespace():
    provider = GeminiProvider()
    result = provider.generate("   ")
    assert result.success is False
    assert result.message == "Prompt is invalid."


def test_invalid_prompt_none():
    provider = GeminiProvider()
    result = provider.generate(None)
    assert result.success is False
    assert result.message == "Prompt is invalid."


def test_invalid_model_type(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    provider = GeminiProvider()
    result = provider.generate("hello", model=123)
    assert result.success is False
    assert result.message == "Gemini model configuration is invalid."


def test_invalid_model_empty(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    provider = GeminiProvider()
    result = provider.generate("hello", model="")
    assert result.success is False
    assert result.message == "Gemini model configuration is invalid."


def test_invalid_model_whitespace(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    provider = GeminiProvider()
    result = provider.generate("hello", model="   ")
    assert result.success is False
    assert result.message == "Gemini model configuration is invalid."


def test_invalid_parameters_type(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    provider = GeminiProvider()
    result = provider.generate("hello", model="gemini-2.0-flash", parameters="bad")
    assert result.success is False
    assert result.message == "Gemini parameters configuration is invalid."


def test_invalid_parameters_list(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    provider = GeminiProvider()
    result = provider.generate("hello", model="gemini-2.0-flash", parameters=[1, 2])
    assert result.success is False
    assert result.message == "Gemini parameters configuration is invalid."


def test_missing_credentials_returns_failure(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = GeminiProvider()
    result = provider.generate("hello", model="gemini-2.0-flash")
    assert result.success is False
    assert result.message == "Gemini credentials are not configured."
    assert result.errors == []


def test_sdk_failure_is_converted_and_secret_is_redacted(monkeypatch):
    secret = "gemini-secret-value"
    models = FakeGeminiModels(error=RuntimeError(secret))
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", secret)
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate("hello", model="gemini-2.0-flash")
    visible = repr(result) + repr(result.errors) + repr(result.metadata)

    expected = Result.fail("Gemini generation failed.")
    assert result.success == expected.success
    assert result.message == expected.message
    assert result.errors == expected.errors
    assert secret not in visible


def test_empty_response_returns_failure(monkeypatch):
    models = FakeGeminiModels(response=empty_response())
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate("hello", model="gemini-2.0-flash")
    expected = Result.fail("Gemini returned an invalid response.")
    assert result.success == expected.success
    assert result.message == expected.message


def test_none_response_returns_failure(monkeypatch):
    models = FakeGeminiModels(response=SimpleNamespace(text=None, candidates=None))
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate("hello", model="gemini-2.0-flash")
    expected = Result.fail("Gemini returned an invalid response.")
    assert result.success == expected.success
    assert result.message == expected.message


def test_parameters_with_blocked_keys_are_rejected(monkeypatch):
    models = FakeGeminiModels(response=successful_response())
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate(
        "hello",
        model="gemini-2.0-flash",
        parameters={"contents": "override"},
    )

    assert result.success is True
    assert models.calls[0]["config"] is None


def test_cloud_ai_registration_lookup_selection_and_invocation(monkeypatch):
    models = FakeGeminiModels(response=successful_response("gemini result"))
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    service = CloudAIService()
    registration = service.register_provider("gemini", provider)
    lookup = service.get_provider("gemini")
    generation = service.generate(
        "hello",
        provider="gemini",
        model="gemini-2.0-flash",
    )

    assert registration.success is True
    assert lookup.success is True
    assert lookup.data is provider
    assert generation.success is True
    assert generation.data == "gemini result"
    assert generation.metadata["provider"] == "gemini"


def test_cloud_ai_lookup_missing_provider_returns_failure():
    result = CloudAIService().get_provider("gemini")
    expected = Result.fail("Provider not registered: gemini")
    assert result.success == expected.success
    assert result.message == expected.message
    assert result.errors == expected.errors


def test_gemini_is_not_default_when_openai_registered_first():
    service = CloudAIService()
    service.register_provider("openai", GeminiProvider())
    service.register_provider("gemini", GeminiProvider())

    list_result = service.list_providers()
    assert list_result.success is True
    assert list_result.metadata["default"] == "openai"


def test_result_ok_compatibility(monkeypatch):
    models = FakeGeminiModels(response=successful_response())
    client = FakeGeminiClient(models)
    provider = GeminiProvider()

    monkeypatch.setenv("GEMINI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.gemini_provider._create_gemini_client",
        lambda api_key: client,
    )

    result = provider.generate("hello", model="gemini-2.0-flash")

    assert isinstance(result, Result)
    assert result.success is True
    assert isinstance(result.data, str)
    assert result.errors == []
    assert isinstance(result.metadata, dict)
    assert isinstance(result.message, str)


def test_result_fail_compatibility(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = GeminiProvider()

    result = provider.generate("hello", model="gemini-2.0-flash")

    assert isinstance(result, Result)
    assert result.success is False
    assert isinstance(result.message, str)
    assert result.errors == []
    assert isinstance(result.metadata, dict)
