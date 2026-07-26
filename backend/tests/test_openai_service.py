from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.config import Settings
from app.services.openai_service import OpenAIService
from app.services.provider import LLMProvider


def build_settings() -> Settings:
    return Settings(
        gemini_api_key="test-key",
        gemini_model="test-model",
        openai_api_key="test-key",
        openai_model="test-openai-model",
        anthropic_api_key="test-key",
        anthropic_model="test-model",
    )


def build_service(output_text: str) -> OpenAIService:
    client = Mock()
    client.responses.create.return_value = SimpleNamespace(
        output_text=output_text
    )
    with patch(
        "app.services.openai_service.OpenAI",
        return_value=client,
    ):
        service = OpenAIService(build_settings())
    return service


def test_openai_service_implements_provider_contract() -> None:
    assert isinstance(build_service("Hello"), LLMProvider)


def test_generate_normalizes_successful_response() -> None:
    service = build_service("Hello")

    result = service.generate("Say hello")

    assert result.provider == "openai"
    assert result.model == "test-openai-model"
    assert result.content == "Hello"
    assert result.latency_ms >= 0
    assert result.error is None
    service.client.responses.create.assert_called_once_with(
        model="test-openai-model",
        input="Say hello",
    )


def test_generate_normalizes_empty_content() -> None:
    result = build_service("").generate("Say hello")

    assert result.content is None
    assert result.error == "The provider returned no text content."


def test_generate_normalizes_sdk_exception() -> None:
    service = build_service("unused")
    service.client.responses.create.side_effect = RuntimeError("offline")

    result = service.generate("Say hello")

    assert result.content is None
    assert result.error == "RuntimeError: offline"
