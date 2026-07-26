from fastapi.testclient import TestClient

import pytest

from app.api.routes import (
    get_anthropic_service,
    get_gemini_service,
    get_openai_service,
)
from app.main import app
from app.schemas import ModelResult
from app.services.provider import LLMProvider


class StubGeminiService(LLMProvider):
    provider_name = "gemini"

    def __init__(self, result: ModelResult) -> None:
        self.result = result
        self.received_prompt: str | None = None

    def generate(self, prompt: str) -> ModelResult:
        self.received_prompt = prompt
        return self.result


client = TestClient(app)


def override_service(service: StubGeminiService) -> None:
    app.dependency_overrides[get_gemini_service] = lambda: service


def teardown_function() -> None:
    app.dependency_overrides.clear()


def test_health_check_does_not_require_provider_configuration() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_compare_returns_normalized_provider_result() -> None:
    service = StubGeminiService(
        ModelResult(
            provider="gemini",
            model="test-model",
            content="A test response",
            latency_ms=42,
        )
    )
    override_service(service)

    response = client.post(
        "/api/v1/compare/gemini",
        json={"prompt": "Explain adapters."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "gemini",
        "model": "test-model",
        "content": "A test response",
        "latency_ms": 42,
        "error": None,
    }
    assert service.received_prompt == "Explain adapters."


def test_compare_preserves_normalized_provider_error() -> None:
    service = StubGeminiService(
        ModelResult(
            provider="gemini",
            model="test-model",
            latency_ms=17,
            error="AuthenticationError: invalid key",
        )
    )
    override_service(service)

    response = client.post(
        "/api/v1/compare/gemini",
        json={"prompt": "Hello"},
    )

    assert response.status_code == 200
    assert response.json()["content"] is None
    assert response.json()["error"] == "AuthenticationError: invalid key"


def test_compare_rejects_empty_prompt_before_calling_provider() -> None:
    service = StubGeminiService(
        ModelResult(
            provider="gemini",
            model="test-model",
            content="unused",
            latency_ms=1,
        )
    )
    override_service(service)

    response = client.post(
        "/api/v1/compare/gemini",
        json={"prompt": ""},
    )

    assert response.status_code == 422
    assert service.received_prompt is None


def test_compare_rejects_prompt_over_maximum_length() -> None:
    response = client.post(
        "/api/v1/compare/gemini",
        json={"prompt": "x" * 20_001},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("path", "dependency", "provider"),
    [
        ("/api/v1/compare/gemini", get_gemini_service, "gemini"),
        ("/api/v1/compare/openai", get_openai_service, "openai"),
        ("/api/v1/compare/claude", get_anthropic_service, "anthropic"),
    ],
)
def test_each_provider_endpoint_uses_its_injected_adapter(
    path: str,
    dependency: object,
    provider: str,
) -> None:
    service = StubGeminiService(
        ModelResult(
            provider=provider,
            model="test-model",
            content="A test response",
            latency_ms=10,
        )
    )
    app.dependency_overrides[dependency] = lambda: service

    response = client.post(path, json={"prompt": "Hello"})

    assert response.status_code == 200
    assert response.json()["provider"] == provider
    assert service.received_prompt == "Hello"
