import time

from openai import OpenAI

from app.config import Settings
from app.schemas import ModelResult
from app.services.provider import LLMProvider


class OpenAIService(LLMProvider):
    provider_name = "openai"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, prompt: str) -> ModelResult:
        started_at = time.perf_counter()

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
            )
            latency_ms = round((time.perf_counter() - started_at) * 1000)
            content = response.output_text

            if not content:
                return ModelResult(
                    provider=self.provider_name,
                    model=self.model,
                    latency_ms=latency_ms,
                    error="The provider returned no text content.",
                )

            return ModelResult(
                provider=self.provider_name,
                model=self.model,
                content=content,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            latency_ms = round((time.perf_counter() - started_at) * 1000)
            return ModelResult(
                provider=self.provider_name,
                model=self.model,
                latency_ms=latency_ms,
                error=f"{type(exc).__name__}: {exc}",
            )
