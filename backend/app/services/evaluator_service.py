from app.schemas import ModelRecommendation, ModelResult


def recommend_model(
    results: list[ModelResult],
) -> ModelRecommendation | None:
    successful = [result for result in results if result.error is None]
    if not successful:
        return None

    max_latency = max(result.latency_ms for result in successful) or 1
    known_costs = [
        result.estimated_cost
        for result in successful
        if result.estimated_cost is not None
    ]
    max_cost = max(known_costs, default=0.0)

    ranked: list[tuple[float, ModelResult]] = []
    for result in successful:
        quality = (result.quality_score or 3.0) / 5
        speed = 1 - (result.latency_ms / max_latency)
        if result.estimated_cost is None or max_cost == 0:
            cost_efficiency = 0.5
        else:
            cost_efficiency = 1 - (result.estimated_cost / max_cost)
        score = quality * 0.6 + speed * 0.2 + cost_efficiency * 0.2
        ranked.append((score, result))

    score, winner = max(ranked, key=lambda item: item[0])
    quality_basis = (
        "manual quality ratings"
        if winner.quality_score is not None
        else "a neutral quality baseline"
    )
    return ModelRecommendation(
        provider=winner.provider,
        score=round(score, 4),
        reason=(
            f"Best combined score using {quality_basis}, latency, and cost. "
            "Add manual ratings to strengthen this recommendation."
        ),
    )
