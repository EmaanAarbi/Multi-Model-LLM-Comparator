from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ComparisonRun(Base):
    __tablename__ = "comparison_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    prompt: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    results: Mapped[list["ProviderResult"]] = relationship(
        back_populates="comparison",
        cascade="all, delete-orphan",
        order_by="ProviderResult.position",
    )


class ProviderResult(Base):
    __tablename__ = "provider_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    comparison_id: Mapped[int] = mapped_column(
        ForeignKey("comparison_runs.id", ondelete="CASCADE"),
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(128))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    accuracy: Mapped[int | None] = mapped_column(nullable=True)
    completeness: Mapped[int | None] = mapped_column(nullable=True)
    format_following: Mapped[int | None] = mapped_column(nullable=True)
    conciseness: Mapped[int | None] = mapped_column(nullable=True)
    usefulness: Mapped[int | None] = mapped_column(nullable=True)
    error_code: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    comparison: Mapped[ComparisonRun] = relationship(
        back_populates="results"
    )
