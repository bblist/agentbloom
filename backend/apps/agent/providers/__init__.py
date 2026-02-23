"""
LLM provider abstraction — swap between OpenAI (GPT-4o), Claude, and Gemini.

Primary: GPT-4o — best tool use, structured output, fast reasoning.
Fallback: Claude 4.6 — creative content, nuanced writing, design.
Design: Claude 4.6 (default) or Gemini 3.2 Pro — both strong at visual/UI tasks.
"""

from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider

PROVIDERS = {
    "openai": OpenAIProvider,
    "claude": ClaudeProvider,
    "gemini": GeminiProvider,
}


def get_provider(provider_name: str, **kwargs) -> BaseLLMProvider:
    """Factory function to get the appropriate LLM provider."""
    provider_class = PROVIDERS.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown LLM provider: {provider_name}. Available: {list(PROVIDERS.keys())}")
    return provider_class(**kwargs)


__all__ = [
    "BaseLLMProvider",
    "OpenAIProvider",
    "ClaudeProvider",
    "GeminiProvider",
    "get_provider",
]
