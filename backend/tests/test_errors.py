import pytest

from app.services.errors import normalize_provider_error


@pytest.mark.parametrize(
    ("exception", "expected_code"),
    [
        (RuntimeError("invalid API key"), "authentication_error"),
        (RuntimeError("quota exceeded"), "rate_limit_error"),
        (TimeoutError("timed out"), "timeout_error"),
        (ConnectionError("offline"), "connection_error"),
        (RuntimeError("unexpected"), "provider_error"),
    ],
)
def test_provider_errors_are_safely_normalized(
    exception: Exception,
    expected_code: str,
) -> None:
    error = normalize_provider_error(exception)

    assert error.code == expected_code
    assert "invalid API key" not in error.message
