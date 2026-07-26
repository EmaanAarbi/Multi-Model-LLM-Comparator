from app.schemas import ModelResult
from app.services.evaluator_service import recommend_model


def test_recommendation_excludes_failed_providers() -> None:
    recommendation = recommend_model(
        [
            ModelResult(
                provider="openai",
                model="model",
                latency_ms=1,
                error="failed",
            ),
            ModelResult(
                provider="gemini",
                model="model",
                content="ok",
                latency_ms=100,
            ),
        ]
    )

    assert recommendation is not None
    assert recommendation.provider == "gemini"


def test_recommendation_prefers_higher_manual_quality() -> None:
    recommendation = recommend_model(
        [
            ModelResult(
                provider="openai",
                model="model",
                content="ok",
                latency_ms=100,
                estimated_cost=0.001,
                quality_score=5,
            ),
            ModelResult(
                provider="gemini",
                model="model",
                content="ok",
                latency_ms=50,
                estimated_cost=0.0005,
                quality_score=2,
            ),
        ]
    )

    assert recommendation is not None
    assert recommendation.provider == "openai"


def test_recommendation_is_none_when_every_provider_failed() -> None:
    assert recommend_model(
        [
            ModelResult(
                provider="openai",
                model="model",
                latency_ms=1,
                error="failed",
            )
        ]
    ) is None
