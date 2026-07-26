from concurrent.futures import ThreadPoolExecutor

from app.schemas import CompareResponse, ModelResult, ProviderName
from app.db.repository import ComparisonRepository
from app.services.evaluator_service import recommend_model
from app.services.provider import LLMProvider


class ComparatorService:
    def __init__(
        self,
        providers: dict[ProviderName, LLMProvider],
        repository: ComparisonRepository | None = None,
    ) -> None:
        self.providers = providers
        self.repository = repository

    def compare(
        self,
        prompt: str,
        selected_providers: list[ProviderName],
    ) -> CompareResponse:
        with ThreadPoolExecutor(
            max_workers=len(selected_providers),
            thread_name_prefix="provider",
        ) as executor:
            futures = {
                provider: executor.submit(
                    self.providers[provider].generate,
                    prompt,
                )
                for provider in selected_providers
            }
            results: list[ModelResult] = []
            for provider in selected_providers:
                try:
                    results.append(futures[provider].result())
                except Exception:
                    adapter = self.providers[provider]
                    results.append(
                        ModelResult(
                            provider=provider,
                            model=getattr(adapter, "model", "unknown"),
                            latency_ms=0,
                            error_code="internal_adapter_error",
                            error="Provider adapter failed unexpectedly.",
                        )
                    )

        comparison_id = None
        if self.repository is not None:
            comparison_id = self.repository.save(prompt, results)

        return CompareResponse(
            comparison_id=comparison_id,
            results=results,
            recommendation=recommend_model(results),
        )
