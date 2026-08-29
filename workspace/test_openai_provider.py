from types import SimpleNamespace

import pytest

from core.result import Result
from providers.openai_provider import OpenAIProvider
from services.cloud_ai_service import CloudAIService


class FakeCompletions:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


class FakeClient:
    def __init__(self, completions):
        self.chat = SimpleNamespace(completions=completions)


def successful_response(content="generated text"):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_construction_and_generic_contract():
    provider = OpenAIProvider()

    assert callable(provider.generate)


def test_success_forwards_model_and_parameters(monkeypatch):
    completions = FakeCompletions(successful_response())
    client = FakeClient(completions)
    provider = OpenAIProvider()

    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.openai_provider._create_openai_client",
        lambda api_key: client,
    )

    result = provider.generate(
        "hello",
        model="test-model",
        parameters={"temperature": 0.2},
    )

    assert result.success is True
    assert result.data == "generated text"
    assert result.errors == []
    assert completions.calls == [
        {
            "model": "test-model",
            "messages": [{"role": "user", "content": "hello"}],
            "temperature": 0.2,
        }
    ]


@pytest.mark.parametrize(
    "prompt, model, parameters, message",
    [
        ("", "test-model", None, "Prompt is invalid."),
        ("hello", "", None, "OpenAI model configuration is invalid."),
        ("hello", "test-model", [], "OpenAI parameters configuration is invalid."),
        ("hello", None, None, "OpenAI model configuration is missing."),
    ],
)
def test_invalid_configuration_returns_failure(
    monkeypatch,
    prompt,
    model,
    parameters,
    message,
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")

    result = OpenAIProvider().generate(
        prompt,
        model=model,
        parameters=parameters,
    )

    expected = Result.fail(message)
    assert result.success == expected.success
    assert result.message == expected.message
    assert result.errors == expected.errors


def test_missing_credentials_returns_failure(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = OpenAIProvider().generate("hello", model="test-model")

    assert result.success is False
    assert result.message == "OpenAI credentials are not configured."
    assert result.errors == []


def test_sdk_failure_is_converted_and_secret_is_redacted(monkeypatch):
    secret = "sdk-secret-value"
    completions = FakeCompletions(error=RuntimeError(secret))
    provider = OpenAIProvider()

    monkeypatch.setenv("OPENAI_API_KEY", secret)
    monkeypatch.setattr(
        "providers.openai_provider._create_openai_client",
        lambda api_key: FakeClient(completions),
    )

    result = provider.generate("hello", model="test-model")
    visible = repr(result) + repr(result.errors) + repr(result.metadata)

    expected = Result.fail("OpenAI generation failed.")
    assert result.success == expected.success
    assert result.message == expected.message
    assert result.errors == expected.errors
    assert secret not in visible


def test_invalid_response_returns_failure(monkeypatch):
    provider = OpenAIProvider()
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.openai_provider._create_openai_client",
        lambda api_key: FakeClient(FakeCompletions(SimpleNamespace(choices=[]))),
    )

    result = provider.generate("hello", model="test-model")

    expected = Result.fail("OpenAI returned an invalid response.")
    assert result.success == expected.success
    assert result.message == expected.message
    assert result.errors == expected.errors


def test_cloud_ai_registration_lookup_selection_and_invocation(monkeypatch):
    completions = FakeCompletions(successful_response("service result"))
    provider = OpenAIProvider()

    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    monkeypatch.setattr(
        "providers.openai_provider._create_openai_client",
        lambda api_key: FakeClient(completions),
    )

    service = CloudAIService()
    registration = service.register_provider("openai", provider)
    lookup = service.get_provider("openai")
    generation = service.generate(
        "hello",
        provider="openai",
        model="test-model",
    )

    assert registration.success is True
    assert lookup.success is True
    assert lookup.data is provider
    assert generation.success is True
    assert generation.data == "service result"
    assert generation.metadata["provider"] == "openai"


def test_cloud_ai_lookup_missing_provider_returns_failure():
    result = CloudAIService().get_provider("openai")

    expected = Result.fail("Provider not registered: openai")
    assert result.success == expected.success
    assert result.message == expected.message
    assert result.errors == expected.errors
