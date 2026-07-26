import time

from app.schemas import ModelResult
from app.services.comparator_service import ComparatorService
from app.services.provider import LLMProvider


class TimedProvider(LLMProvider):
    def __init__(self, provider_name: str, delay: float) -> None:
        self.provider_name = provider_name
        self.delay = delay

    def generate(self, prompt: str) -> ModelResult:
        time.sleep(self.delay)
        return ModelResult(
            provider=self.provider_name,
            model=f"{self.provider_name}-model",
            content=prompt,
            latency_ms=round(self.delay * 1_000),
        )


def test_compare_runs_providers_concurrently_and_preserves_order() -> None:
    service = ComparatorService(
        providers={
            "gemini": TimedProvider("gemini", 0.1),
            "openai": TimedProvider("openai", 0.1),
            "anthropic": TimedProvider("anthropic", 0.1),
        }
    )

    started_at = time.perf_counter()
    response = service.compare(
        "Hello",
        ["anthropic", "gemini", "openai"],
    )
    elapsed = time.perf_counter() - started_at

    assert elapsed < 0.25
    assert [result.provider for result in response.results] == [
        "anthropic",
        "gemini",
        "openai",
    ]


def test_compare_preserves_partial_provider_failure() -> None:
    failing_result = ModelResult(
        provider="openai",
        model="test-model",
        latency_ms=10,
        error="RateLimitError",
    )

    class FailingProvider(LLMProvider):
        provider_name = "openai"

        def generate(self, prompt: str) -> ModelResult:
            return failing_result

    service = ComparatorService(
        providers={"openai": FailingProvider()}
    )

    response = service.compare("Hello", ["openai"])

    assert response.results == [failing_result]
