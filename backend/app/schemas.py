from typing import Literal
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


ProviderName = Literal["gemini", "openai", "anthropic"]


class CompareRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=20_000,
        description="Prompt sent to the configured language model.",
    )


GeminiCompareRequest = CompareRequest


class MultiCompareRequest(CompareRequest):
    providers: list[ProviderName] = Field(min_length=1, max_length=3)

    @field_validator("providers")
    @classmethod
    def providers_must_be_unique(
        cls,
        providers: list[ProviderName],
    ) -> list[ProviderName]:
        if len(providers) != len(set(providers)):
            raise ValueError("Providers must be unique.")
        return providers


class ModelResult(BaseModel):
    provider: str
    model: str
    content: str | None = None
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost: float | None = None
    quality_score: float | None = None
    error_code: str | None = None
    error: str | None = None


class ModelRecommendation(BaseModel):
    provider: str
    score: float
    reason: str


class CompareResponse(BaseModel):
    comparison_id: int | None = None
    results: list[ModelResult]
    recommendation: ModelRecommendation | None = None


class ComparisonHistoryItem(BaseModel):
    id: int
    prompt: str
    created_at: datetime
    results: list[ModelResult]
    recommendation: ModelRecommendation | None = None


class RatingRequest(BaseModel):
    accuracy: int = Field(ge=1, le=5)
    completeness: int = Field(ge=1, le=5)
    format_following: int = Field(ge=1, le=5)
    conciseness: int = Field(ge=1, le=5)
    usefulness: int = Field(ge=1, le=5)
