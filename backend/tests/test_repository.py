from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Base
from app.db.repository import ComparisonRepository
from app.schemas import ModelResult
from app.schemas import RatingRequest


def build_repository() -> ComparisonRepository:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return ComparisonRepository(Session(engine))


def test_repository_saves_and_reads_comparison() -> None:
    repository = build_repository()
    result = ModelResult(
        provider="gemini",
        model="gemini-2.5-flash",
        content="Hello",
        latency_ms=100,
        input_tokens=5,
        output_tokens=2,
        estimated_cost=0.0000065,
    )

    comparison_id = repository.save("Say hello", [result])
    comparison = repository.get(comparison_id)

    assert comparison is not None
    assert comparison.prompt == "Say hello"
    assert comparison.results == [result]


def test_repository_lists_newest_comparison_first() -> None:
    repository = build_repository()
    result = ModelResult(
        provider="openai",
        model="test-model",
        content="Hello",
        latency_ms=10,
    )
    first_id = repository.save("First", [result])
    second_id = repository.save("Second", [result])

    history = repository.list_recent()

    assert [item.id for item in history] == [second_id, first_id]


def test_repository_returns_none_for_unknown_id() -> None:
    repository = build_repository()

    assert repository.get(999) is None


def test_repository_calculates_and_persists_manual_quality_score() -> None:
    repository = build_repository()
    result = ModelResult(
        provider="gemini",
        model="model",
        content="Hello",
        latency_ms=10,
    )
    comparison_id = repository.save("Hello", [result])

    rated = repository.rate(
        comparison_id,
        "gemini",
        RatingRequest(
            accuracy=5,
            completeness=4,
            format_following=5,
            conciseness=4,
            usefulness=5,
        ),
    )

    assert rated is not None
    assert rated.quality_score == 4.6
