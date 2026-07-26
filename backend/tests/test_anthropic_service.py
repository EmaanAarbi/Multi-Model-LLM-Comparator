from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.config import Settings
from app.services.anthropic_service import AnthropicService
from app.services.provider import LLMProvider


def build_settings() -> Settings:
    return Settings(
        gemini_api_key="test-key",
        gemini_model="test-model",
        openai_api_key="test-key",
        openai_model="test-model",
        anthropic_api_key="test-key",
        anthropic_model="test-anthropic-model",
    )


def build_service(content: list[object]) -> AnthropicService:
    client = Mock()
    client.messages.create.return_value = SimpleNamespace(content=content)
    with patch(
        "app.services.anthropic_service.Anthropic",
        return_value=client,
    ):
        service = AnthropicService(build_settings())
    return service


def text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def test_anthropic_service_implements_provider_contract() -> None:
    assert isinstance(build_service([text_block("Hello")]), LLMProvider)


def test_generate_normalizes_successful_response() -> None:
    service = build_service([text_block("Hello"), text_block(" world")])

    result = service.generate("Say hello")

    assert result.provider == "anthropic"
    assert result.model == "test-anthropic-model"
    assert result.content == "Hello world"
    assert result.latency_ms >= 0
    assert result.error is None
    service.client.messages.create.assert_called_once_with(
        model="test-anthropic-model",
        max_tokens=1_024,
        messages=[{"role": "user", "content": "Say hello"}],
    )


def test_generate_ignores_non_text_blocks() -> None:
    result = build_service(
        [SimpleNamespace(type="tool_use"), text_block("Hello")]
    ).generate("Say hello")

    assert result.content == "Hello"


def test_generate_normalizes_empty_content() -> None:
    result = build_service([]).generate("Say hello")

    assert result.content is None
    assert result.error == "The provider returned no text content."


def test_generate_normalizes_sdk_exception() -> None:
    service = build_service([text_block("unused")])
    service.client.messages.create.side_effect = RuntimeError("offline")

    result = service.generate("Say hello")

    assert result.content is None
    assert result.error == "RuntimeError: offline"
