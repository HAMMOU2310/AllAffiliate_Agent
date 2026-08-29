"""Unit tests for CloudAIContentGenerator adapter."""

from types import SimpleNamespace

import pytest

from core.result import Result
from providers.cloud_ai_content_generator import CloudAIContentGenerator


class FakeCloudAIService:
    """Stub CloudAIService for unit tests."""

    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.calls = []

    def generate(self, prompt=None, model=None, parameters=None):
        self.calls.append(
            {"prompt": prompt, "model": model, "parameters": parameters}
        )
        if self._error is not None:
            raise self._error
        return self._response


def ok_response(text="TITLE: Test Title\nBODY: Test body content.\nCLAIMS: none"):
    return Result.ok(data=text, message="AI generation completed.")


def fail_response(message="provider failed"):
    return Result.fail(message)


def test_construction():
    service = FakeCloudAIService()
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    assert generator._service is service
    assert generator._model == "test-model"


def test_basic_generation():
    service = FakeCloudAIService(response=ok_response())
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is True
    assert result.data["title"] == "Test Title"
    assert result.data["body"] == "Test body content."
    assert isinstance(result.data["claims"], list)
    assert len(service.calls) == 1
    assert service.calls[0]["model"] == "test-model"


def test_generation_with_persona():
    service = FakeCloudAIService(response=ok_response())
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    persona = {"audience": "developers", "tone": "professional"}
    result = generator.generate("Write about AI.", persona=persona)

    assert result.success is True
    prompt_used = service.calls[0]["prompt"]
    assert "developers" in prompt_used
    assert "professional" in prompt_used


def test_generation_with_format():
    service = FakeCloudAIService(response=ok_response())
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.", format="blog post")

    assert result.success is True
    prompt_used = service.calls[0]["prompt"]
    assert "blog post" in prompt_used


def test_generation_with_persona_and_format():
    service = FakeCloudAIService(response=ok_response())
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    persona = {"tone": "casual"}
    result = generator.generate("Write about AI.", persona=persona, format="tweet")

    assert result.success is True
    prompt_used = service.calls[0]["prompt"]
    assert "casual" in prompt_used
    assert "tweet" in prompt_used


def test_invalid_brief_empty():
    service = FakeCloudAIService()
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("")

    assert result.success is False
    assert result.message == "Content brief is invalid."
    assert len(service.calls) == 0


def test_invalid_brief_whitespace():
    service = FakeCloudAIService()
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("   ")

    assert result.success is False
    assert result.message == "Content brief is invalid."


def test_invalid_brief_none():
    service = FakeCloudAIService()
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate(None)

    assert result.success is False
    assert result.message == "Content brief is invalid."


def test_invalid_persona():
    service = FakeCloudAIService()
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.", persona="not a dict")

    assert result.success is False
    assert result.message == "Content persona is invalid."


def test_invalid_format():
    service = FakeCloudAIService()
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.", format=123)

    assert result.success is False
    assert result.message == "Content format is invalid."


def test_cloud_ai_failure():
    service = FakeCloudAIService(response=fail_response("provider error"))
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is False
    assert result.message == "provider error"


def test_cloud_ai_exception():
    service = FakeCloudAIService(error=RuntimeError("SDK crash"))
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is False
    assert result.message == "Cloud AI service execution failed."


def test_cloud_ai_returns_invalid_type():
    service = SimpleNamespace(generate=lambda **kw: "not a result")
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is False
    assert result.message == "Cloud AI service returned an invalid Result."


def test_no_service_registered():
    generator = CloudAIContentGenerator(cloud_ai_service=None, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is False
    assert result.message == "No Cloud AI service is registered."


def test_service_missing_generate_method():
    service = SimpleNamespace()
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is False
    assert result.message == "Cloud AI service is invalid."


def test_malformed_response_no_title():
    service = FakeCloudAIService(response=Result.ok(data="Just some text without structure."))
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is False
    assert result.message == "Cloud AI service returned malformed content."


def test_malformed_response_no_body():
    service = FakeCloudAIService(response=Result.ok(data="TITLE: Only Title"))
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    assert result.success is False
    assert result.message == "Cloud AI service returned malformed content."


def test_result_compatibility_with_content_service():
    from services.content_service import ContentService

    response_text = (
        "TITLE: AI Revolution\n"
        "BODY: Artificial intelligence is transforming industries worldwide.\n"
        "CLAIMS: AI is growing; industries are changing"
    )
    service = FakeCloudAIService(response=ok_response(response_text))
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")
    content_service = ContentService(generator)

    result = content_service.create("Write about AI trends.")

    assert result.success is True
    assert result.data["title"] == "AI Revolution"
    assert "transforming" in result.data["body"]
    assert len(result.data["claims"]) == 2


def test_model_forwarded_to_cloud_ai():
    service = FakeCloudAIService(response=ok_response())
    generator = CloudAIContentGenerator(
        cloud_ai_service=service, model="gpt-4o", parameters={"temperature": 0.7}
    )

    generator.generate("Write about AI.")

    assert service.calls[0]["model"] == "gpt-4o"
    assert service.calls[0]["parameters"] == {"temperature": 0.7}


def test_secret_not_in_result(monkeypatch):
    secret = "sk-test-secret-key-12345"
    monkeypatch.setenv("OPENAI_API_KEY", secret)

    service = FakeCloudAIService(response=ok_response())
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about AI.")

    visible = repr(result) + repr(result.errors) + repr(result.metadata)
    assert secret not in visible


def test_metadata_contains_model():
    service = FakeCloudAIService(response=ok_response())
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="gpt-4o-mini")

    result = generator.generate("Write about AI.", format="article")

    assert result.metadata["model"] == "gpt-4o-mini"
    assert result.metadata["format"] == "article"


def test_claims_extraction_from_semicolons():
    response_text = (
        "TITLE: Tech Trends\n"
        "BODY: Technology is evolving rapidly.\n"
        "CLAIMS: AI is growing; Cloud is expanding; Security matters"
    )
    service = FakeCloudAIService(response=ok_response(response_text))
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write about tech.")

    assert result.success is True
    assert len(result.data["claims"]) == 3
    assert "AI is growing" in result.data["claims"]


def test_claims_none_returns_empty():
    response_text = (
        "TITLE: Opinion Piece\n"
        "BODY: This is my opinion on the matter.\n"
        "CLAIMS: NONE"
    )
    service = FakeCloudAIService(response=ok_response(response_text))
    generator = CloudAIContentGenerator(cloud_ai_service=service, model="test-model")

    result = generator.generate("Write an opinion.")

    assert result.success is True
    assert result.data["claims"] == []
