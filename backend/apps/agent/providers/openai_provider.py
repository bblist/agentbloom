"""OpenAI GPT provider — primary LLM."""

import json
import logging
import time
from typing import AsyncIterator

from django.conf import settings

from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider using the openai SDK. Primary LLM (GPT-4o)."""

    provider_name = "openai"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _format_tools_for_provider(self, tools: list | None):
        """Convert tool definitions to OpenAI function calling format."""
        if not tools:
            return None
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
            }
            for t in tools
        ]

    async def generate(self, messages: list, tools: list | None = None) -> dict:
        self._log_request(messages, tools)
        start = time.monotonic()

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        formatted = self._format_tools_for_provider(tools)
        if formatted:
            kwargs["tools"] = formatted
            kwargs["tool_choice"] = "auto"

        try:
            response = await self.client.chat.completions.create(**kwargs)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

        latency_ms = int((time.monotonic() - start) * 1000)
        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                })

        return {
            "content": message.content or "",
            "tool_calls": tool_calls,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "model": response.model,
            "latency_ms": latency_ms,
            "finish_reason": choice.finish_reason,
        }

    async def stream(self, messages: list, tools: list | None = None) -> AsyncIterator[dict]:
        self._log_request(messages, tools)
        start = time.monotonic()

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        formatted = self._format_tools_for_provider(tools)
        if formatted:
            kwargs["tools"] = formatted
            kwargs["tool_choice"] = "auto"

        try:
            stream = await self.client.chat.completions.create(**kwargs)
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield {"type": "error", "error": str(e)}
            return

        full_content = ""
        tool_call_buffers = {}  # id -> {name, arguments_str}

        async for chunk in stream:
            if not chunk.choices:
                # Final chunk with usage
                if chunk.usage:
                    yield {
                        "type": "done",
                        "content": full_content,
                        "usage": {
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens,
                        },
                        "latency_ms": int((time.monotonic() - start) * 1000),
                    }
                continue

            delta = chunk.choices[0].delta

            # Content tokens
            if delta.content:
                full_content += delta.content
                yield {"type": "token", "content": delta.content}

            # Tool call deltas
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in tool_call_buffers:
                        tool_call_buffers[idx] = {
                            "id": tc_delta.id or "",
                            "name": tc_delta.function.name if tc_delta.function and tc_delta.function.name else "",
                            "arguments_str": "",
                        }
                    buf = tool_call_buffers[idx]
                    if tc_delta.id:
                        buf["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            buf["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            buf["arguments_str"] += tc_delta.function.arguments

            # Check finish reason
            if chunk.choices[0].finish_reason == "tool_calls":
                for buf in tool_call_buffers.values():
                    try:
                        args = json.loads(buf["arguments_str"])
                    except json.JSONDecodeError:
                        args = {}
                    yield {
                        "type": "tool_call",
                        "tool_call": {
                            "id": buf["id"],
                            "name": buf["name"],
                            "arguments": args,
                        },
                    }

        # If no usage chunk came, send done anyway
        if not full_content and not tool_call_buffers:
            yield {"type": "done", "content": "", "latency_ms": int((time.monotonic() - start) * 1000)}
