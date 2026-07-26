from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.config import Settings
from app.services.gemini_service import GeminiService
from app.services.provider import LLMProvider


def build_service(response: object) -> GeminiService:
    settings = Settings(
        gemini_api_key="test-key",
        gemini_model="test-model",
        openai_api_key="test-key",
        openai_model="test-model",
        anthropic_api_key="test-key",
        anthropic_model="test-model",
    )
    client = Mock()
    client.models.generate_content.return_value = response

    with patch("app.services.gemini_service.genai.Client", return_value=client):
        service = GeminiService(settings)

    return service


def test_gemini_service_implements_provider_contract() -> None:
    service = build_service(SimpleNamespace(text="Hello"))

    assert isinstance(service, LLMProvider)


def test_generate_normalizes_successful_response() -> None:
    service = build_service(SimpleNamespace(text="Hello"))

    result = service.generate("Say hello")

    assert result.provider == "gemini"
    assert result.model == "test-model"
    assert result.content == "Hello"
    assert result.latency_ms >= 0
    assert result.error is None
    service.client.models.generate_content.assert_called_once_with(
        model="test-model",
        contents="Say hello",
    )


def test_generate_normalizes_empty_content() -> None:
    service = build_service(SimpleNamespace(text=""))

    result = service.generate("Say hello")

    assert result.content is None
    assert result.error == "The provider returned no text content."


def test_generate_normalizes_sdk_exception() -> None:
    service = build_service(SimpleNamespace(text="unused"))
    service.client.models.generate_content.side_effect = RuntimeError("offline")

    result = service.generate("Say hello")

    assert result.content is None
    assert result.latency_ms >= 0
    assert result.error == "RuntimeError: offline"
