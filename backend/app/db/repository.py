from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import ComparisonRun, ProviderResult
from app.schemas import (
    CompareResponse,
    ComparisonHistoryItem,
    ModelResult,
    RatingRequest,
)
from app.services.evaluator_service import recommend_model


class ComparisonRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self,
        prompt: str,
        results: list[ModelResult],
    ) -> int:
        comparison = ComparisonRun(prompt=prompt)
        comparison.results = [
            ProviderResult(position=position, **result.model_dump())
            for position, result in enumerate(results)
        ]
        self.session.add(comparison)
        self.session.commit()
        return comparison.id

    def list_recent(self, limit: int = 50) -> list[ComparisonHistoryItem]:
        statement = (
            select(ComparisonRun)
            .options(selectinload(ComparisonRun.results))
            .order_by(ComparisonRun.created_at.desc())
            .limit(limit)
        )
        comparisons = self.session.scalars(statement).all()
        return [self._to_history_item(item) for item in comparisons]

    def get(self, comparison_id: int) -> ComparisonHistoryItem | None:
        statement = (
            select(ComparisonRun)
            .options(selectinload(ComparisonRun.results))
            .where(ComparisonRun.id == comparison_id)
        )
        comparison = self.session.scalar(statement)
        if comparison is None:
            return None
        return self._to_history_item(comparison)

    def rate(
        self,
        comparison_id: int,
        provider: str,
        rating: RatingRequest,
    ) -> ModelResult | None:
        statement = select(ProviderResult).where(
            ProviderResult.comparison_id == comparison_id,
            ProviderResult.provider == provider,
        )
        result = self.session.scalar(statement)
        if result is None:
            return None

        scores = rating.model_dump()
        for field, value in scores.items():
            setattr(result, field, value)
        result.quality_score = round(sum(scores.values()) / len(scores), 2)
        self.session.commit()
        return self._to_model_result(result)

    @staticmethod
    def _to_history_item(
        comparison: ComparisonRun,
    ) -> ComparisonHistoryItem:
        results = [
            ComparisonRepository._to_model_result(result)
            for result in comparison.results
        ]
        return ComparisonHistoryItem(
            id=comparison.id,
            prompt=comparison.prompt,
            created_at=comparison.created_at,
            results=results,
            recommendation=recommend_model(results),
        )

    @staticmethod
    def _to_model_result(result: ProviderResult) -> ModelResult:
        return ModelResult(
            provider=result.provider,
            model=result.model,
            content=result.content,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            estimated_cost=result.estimated_cost,
            quality_score=result.quality_score,
            error_code=result.error_code,
            error=result.error,
        )
