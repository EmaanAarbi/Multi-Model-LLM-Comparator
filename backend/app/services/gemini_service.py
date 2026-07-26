import time

from google import genai

from app.config import Settings
from app.schemas import ModelResult
from app.services.cost_service import estimate_cost
from app.services.errors import normalize_provider_error
from app.services.provider import LLMProvider


class GeminiService(LLMProvider):
    provider_name = "gemini"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.gemini_model
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate(self, prompt: str) -> ModelResult:
        started_at = time.perf_counter()

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            latency_ms = round(
                (time.perf_counter() - started_at) * 1000
            )

            content = response.text
            usage = response.usage_metadata
            input_tokens = getattr(usage, "prompt_token_count", None)
            output_tokens = getattr(usage, "candidates_token_count", None)

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
            latency_ms = round(
                (time.perf_counter() - started_at) * 1000
            )
            error = normalize_provider_error(exc)

            return ModelResult(
                provider=self.provider_name,
                model=self.model,
                latency_ms=latency_ms,
                error_code=error.code,
                error=error.message,
            )
