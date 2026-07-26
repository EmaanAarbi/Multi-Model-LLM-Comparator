from app.services.cost_service import estimate_cost


def test_estimate_cost_uses_input_and_output_prices() -> None:
    assert estimate_cost("gpt-5.6-luna", 1_000_000, 1_000_000) == 7.0


def test_estimate_cost_returns_none_for_unknown_model() -> None:
    assert estimate_cost("unknown-model", 100, 100) is None


def test_estimate_cost_returns_none_for_missing_usage() -> None:
    assert estimate_cost("gpt-5.6-luna", None, 100) is None
