from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas import CompareRequest, ModelResult
from app.services.anthropic_service import AnthropicService
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
