from abc import ABC, abstractmethod

from app.schemas import ModelResult


class LLMProvider(ABC):
    """Contract implemented by every model provider adapter."""

    provider_name: str

    @abstractmethod
    def generate(self, prompt: str) -> ModelResult:
        """Generate a normalized result for a prompt."""
