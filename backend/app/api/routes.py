from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.database import get_db_session
from app.db.repository import ComparisonRepository
from app.schemas import (
    CompareRequest,
    CompareResponse,
    ComparisonHistoryItem,
    ModelResult,
    RatingRequest,
)
from app.schemas import MultiCompareRequest
from app.services.anthropic_service import AnthropicService
from app.services.comparator_service import ComparatorService
from app.services.gemini_service import GeminiService
from app.services.openai_service import OpenAIService
from app.services.provider import LLMProvider


router = APIRouter(prefix="/api/v1/compare", tags=["comparison"])


def get_gemini_service(
    settings: Settings = Depends(get_settings),
) -> LLMProvider:
    return GeminiService(settings)


def get_openai_service(
    settings: Settings = Depends(get_settings),
) -> LLMProvider:
    return OpenAIService(settings)


def get_anthropic_service(
    settings: Settings = Depends(get_settings),
) -> LLMProvider:
    return AnthropicService(settings)


def get_comparator_service(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_db_session),
) -> ComparatorService:
    return ComparatorService(
        providers={
            "gemini": GeminiService(settings),
            "openai": OpenAIService(settings),
            "anthropic": AnthropicService(settings),
        },
        repository=ComparisonRepository(session),
    )


@router.post("", response_model=CompareResponse)
def compare_models(
    request: MultiCompareRequest,
    service: ComparatorService = Depends(get_comparator_service),
) -> CompareResponse:
    return service.compare(request.prompt, request.providers)


@router.get(
    "/history",
    response_model=list[ComparisonHistoryItem],
)
def list_comparisons(
    session: Session = Depends(get_db_session),
) -> list[ComparisonHistoryItem]:
    return ComparisonRepository(session).list_recent()


@router.get(
    "/history/{comparison_id}",
    response_model=ComparisonHistoryItem,
)
def get_comparison(
    comparison_id: int,
    session: Session = Depends(get_db_session),
) -> ComparisonHistoryItem:
    comparison = ComparisonRepository(session).get(comparison_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail="Comparison not found.")
    return comparison


@router.put(
    "/history/{comparison_id}/ratings/{provider}",
    response_model=ModelResult,
)
def rate_comparison_result(
    comparison_id: int,
    provider: str,
    rating: RatingRequest,
    session: Session = Depends(get_db_session),
) -> ModelResult:
    result = ComparisonRepository(session).rate(
        comparison_id,
        provider,
        rating,
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Comparison result not found.",
        )
    return result


@router.post("/gemini", response_model=ModelResult)
def compare_with_gemini(
    request: CompareRequest,
    service: LLMProvider = Depends(get_gemini_service),
) -> ModelResult:
    return service.generate(request.prompt)


@router.post("/openai", response_model=ModelResult)
def compare_with_openai(
    request: CompareRequest,
    service: LLMProvider = Depends(get_openai_service),
) -> ModelResult:
    return service.generate(request.prompt)


@router.post("/claude", response_model=ModelResult)
def compare_with_claude(
    request: CompareRequest,
    service: LLMProvider = Depends(get_anthropic_service),
) -> ModelResult:
    return service.generate(request.prompt)
