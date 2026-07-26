import time

from anthropic import Anthropic

from app.config import Settings
from app.schemas import ModelResult
from app.services.cost_service import estimate_cost
from app.services.errors import normalize_provider_error
from app.services.provider import LLMProvider


class AnthropicService(LLMProvider):
    provider_name = "anthropic"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.anthropic_model
        self.client = Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=30.0,
            max_retries=2,
        )

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
            usage = response.usage
            input_tokens = getattr(usage, "input_tokens", None)
            output_tokens = getattr(usage, "output_tokens", None)

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
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=estimate_cost(
                    self.model,
                    input_tokens,
                    output_tokens,
                ),
            )
        except Exception as exc:
            latency_ms = round((time.perf_counter() - started_at) * 1000)
            error = normalize_provider_error(exc)
            return ModelResult(
                provider=self.provider_name,
                model=self.model,
                latency_ms=latency_ms,
                error_code=error.code,
                error=error.message,
            )
