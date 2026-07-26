from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedError:
    code: str
    message: str


def normalize_provider_error(exc: Exception) -> NormalizedError:
    name = type(exc).__name__.lower()
    details = str(exc).lower()

    if "authentication" in name or "api key" in details:
        return NormalizedError(
            code="authentication_error",
            message="Provider authentication failed.",
        )
    if "ratelimit" in name or "rate limit" in details or "quota" in details:
        return NormalizedError(
            code="rate_limit_error",
            message="Provider quota or rate limit exceeded.",
        )
    if "timeout" in name or "timed out" in details:
        return NormalizedError(
            code="timeout_error",
            message="Provider request timed out.",
        )
    if "connection" in name or "network" in details:
        return NormalizedError(
            code="connection_error",
            message="Could not connect to the provider.",
        )
    if (
        "badrequest" in name
        or "invalidrequest" in name
        or "invalid request" in details
    ):
        return NormalizedError(
            code="invalid_request_error",
            message="Provider rejected the request.",
        )
    return NormalizedError(
        code="provider_error",
        message="Provider request failed.",
    )
