"""Base LLM provider class."""

import json
import logging
import time
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)


class BaseLLMProvider:
    """Base class for all LLM providers."""

    provider_name: str = "base"

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: list, tools: list | None = None) -> dict:
        """
        Generate a response from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions (JSON Schema).

        Returns:
            dict with keys:
              - content: str (response text)
              - tool_calls: list of dicts (tool invocations)
              - usage: dict with prompt_tokens, completion_tokens, total_tokens
              - model: str (model used)
              - latency_ms: int
        """
        raise NotImplementedError

    async def stream(self, messages: list, tools: list | None = None) -> AsyncIterator[dict]:
        """
        Stream a response token-by-token.

        Yields dicts with:
          - type: "token" | "tool_call" | "done" | "error"
          - content: str (for token type)
          - tool_call: dict (for tool_call type)
          - usage: dict (for done type)
        """
        raise NotImplementedError

    def _format_tools_for_provider(self, tools: list | None) -> Any:
        """Format tools into provider-specific schema. Override per provider."""
        return tools

    def _log_request(self, messages: list, tools: list | None):
        msg_summary = f"{len(messages)} messages"
        tool_summary = f"{len(tools)} tools" if tools else "no tools"
        logger.info(f"{self.provider_name}.generate: {msg_summary}, {tool_summary}, model={self.model}")
