import time

from anthropic import Anthropic

from app.config import Settings
from app.schemas import ModelResult
from app.services.provider import LLMProvider


class AnthropicService(LLMProvider):
    provider_name = "anthropic"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.anthropic_model
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def generate(self, prompt: str) -> ModelResult:
        started_at = time.perf_counter()

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1_024,
                messages=[{"role": "user", "content": prompt}],
            )
            latency_ms = round((time.perf_counter() - started_at) * 1000)
            content = "".join(
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            )

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
