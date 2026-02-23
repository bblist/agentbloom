"""
LLM provider abstraction — swap between Gemini, Claude, etc.
"""

import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider:
    """Base class for LLM providers."""

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: list, tools: list = None) -> dict:
        raise NotImplementedError

    async def stream(self, messages: list, tools: list = None):
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider — primary LLM."""

    async def generate(self, messages, tools=None):
        # TODO: Implement Gemini API call
        logger.info(f"GeminiProvider.generate called with model={self.model}")
        return {"content": "Gemini provider not yet implemented", "tool_calls": []}

    async def stream(self, messages, tools=None):
        # TODO: Implement streaming
        yield {"type": "token", "content": "Gemini streaming not yet implemented"}
        yield {"type": "done"}


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider — fallback LLM."""

    async def generate(self, messages, tools=None):
        # TODO: Implement Claude API call
        logger.info(f"ClaudeProvider.generate called with model={self.model}")
        return {"content": "Claude provider not yet implemented", "tool_calls": []}

    async def stream(self, messages, tools=None):
        yield {"type": "token", "content": "Claude streaming not yet implemented"}
        yield {"type": "done"}


def get_provider(provider_name: str, **kwargs) -> BaseLLMProvider:
    """Factory function to get the appropriate LLM provider."""
    providers = {
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
    }
    provider_class = providers.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    return provider_class(**kwargs)
