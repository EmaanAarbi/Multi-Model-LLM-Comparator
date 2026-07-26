from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=20_000,
        description="Prompt sent to the configured language model.",
    )


GeminiCompareRequest = CompareRequest


class ModelResult(BaseModel):
    provider: str
    model: str
    content: str | None = None
    latency_ms: int
    error: str | None = None
