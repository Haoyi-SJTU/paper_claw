"""Unified LLM client using LiteLLM."""

from litellm import completion
from literature_claw.config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    DEFAULT_MODEL,
    AVAILABLE_MODELS,
)


class LLMClient:
    """Unified client for multiple LLM providers via LiteLLM."""

    def __init__(self, model: str | None = None):
        self.model = model or DEFAULT_MODEL
        self._api_keys = {
            "openai": OPENAI_API_KEY,
            "anthropic": ANTHROPIC_API_KEY,
        }

    def _get_api_key(self) -> str | None:
        """Return the API key for the current model's provider."""
        litellm_model = AVAILABLE_MODELS.get(self.model, self.model)
        provider = litellm_model.split("/")[0]
        return self._api_keys.get(provider)

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat completion request and return the response text."""
        litellm_model = AVAILABLE_MODELS.get(self.model, self.model)
        api_key = self._get_api_key()

        response = completion(
            model=litellm_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )
        return response.choices[0].message.content

    def set_model(self, model: str) -> None:
        """Switch to a different model."""
        self.model = model


# Global client instance
_client: LLMClient | None = None


def get_client(model: str | None = None) -> LLMClient:
    """Get or create the global LLM client."""
    global _client
    if _client is None or model is not None:
        _client = LLMClient(model)
    return _client
