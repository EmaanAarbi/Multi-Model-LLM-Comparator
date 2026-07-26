from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    output_per_million: float


MODEL_PRICING: dict[str, ModelPrice] = {
    "gpt-5.6-sol": ModelPrice(5.00, 30.00),
    "gpt-5.6": ModelPrice(5.00, 30.00),
    "gpt-5.6-terra": ModelPrice(2.50, 15.00),
    "gpt-5.6-luna": ModelPrice(1.00, 6.00),
    "gemini-2.5-flash": ModelPrice(0.30, 2.50),
    "claude-opus-4.1": ModelPrice(15.00, 75.00),
}


def estimate_cost(
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    price = MODEL_PRICING.get(model)
    if price is None or input_tokens is None or output_tokens is None:
        return None

    cost = (
        input_tokens * price.input_per_million
        + output_tokens * price.output_per_million
    ) / 1_000_000
    return round(cost, 8)
