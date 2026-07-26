from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Multi-Model LLM Comparator API",
    version="0.1.0",
    description=(
        "Compare language models using normalized performance, "
        "cost, reliability, and quality metrics."
    ),
)

app.include_router(router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}