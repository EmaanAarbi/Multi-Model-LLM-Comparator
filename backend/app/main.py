from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.database import engine
from app.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Multi-Model LLM Comparator API",
    version="0.1.0",
    description=(
        "Compare language models using normalized performance, "
        "cost, reliability, and quality metrics."
    ),
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
