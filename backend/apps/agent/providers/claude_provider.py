"""Anthropic Claude provider — fallback + design LLM."""

import json
import logging
import time
from typing import AsyncIterator

from django.conf import settings

from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider (Claude 4.6). Fallback + design tasks."""

    provider_name = "claude"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    def _format_tools_for_provider(self, tools: list | None):
        """Convert tool definitions to Anthropic tool format."""
        if not tools:
            return None
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"],
            }
            for t in tools
        ]

    def _convert_messages(self, messages: list) -> tuple[str, list]:
        """
        Split messages into system prompt and message list.
        Anthropic requires system as a top-level param, not in messages.
        """
        system_prompt = ""
        converted = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt += msg["content"] + "\n"
            elif msg["role"] == "tool":
                # Anthropic uses tool_result content blocks
                converted.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.get("tool_call_id", ""),
                            "content": msg["content"],
                        }
                    ],
                })
            else:
                converted.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })
        return system_prompt.strip(), converted

    async def generate(self, messages: list, tools: list | None = None) -> dict:
        self._log_request(messages, tools)
        start = time.monotonic()

        system_prompt, converted_messages = self._convert_messages(messages)

        kwargs = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        formatted_tools = self._format_tools_for_provider(tools)
        if formatted_tools:
            kwargs["tools"] = formatted_tools

        try:
            response = await self.client.messages.create(**kwargs)
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

        latency_ms = int((time.monotonic() - start) * 1000)

        content = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input,
                })

        return {
            "content": content,
            "tool_calls": tool_calls,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            "model": response.model,
            "latency_ms": latency_ms,
            "finish_reason": response.stop_reason,
        }

    async def stream(self, messages: list, tools: list | None = None) -> AsyncIterator[dict]:
        self._log_request(messages, tools)
        start = time.monotonic()

        system_prompt, converted_messages = self._convert_messages(messages)

        kwargs = {
            "model": self.model,
            "messages": converted_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        formatted_tools = self._format_tools_for_provider(tools)
        if formatted_tools:
            kwargs["tools"] = formatted_tools

        try:
            async with self.client.messages.stream(**kwargs) as stream:
                full_content = ""
                tool_calls = []
                current_tool = None

                async for event in stream:
                    if event.type == "content_block_start":
                        if hasattr(event.content_block, "type"):
                            if event.content_block.type == "tool_use":
                                current_tool = {
                                    "id": event.content_block.id,
                                    "name": event.content_block.name,
                                    "arguments_str": "",
                                }
                    elif event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            full_content += event.delta.text
                            yield {"type": "token", "content": event.delta.text}
                        elif hasattr(event.delta, "partial_json"):
                            if current_tool:
                                current_tool["arguments_str"] += event.delta.partial_json
                    elif event.type == "content_block_stop":
                        if current_tool:
                            try:
                                args = json.loads(current_tool["arguments_str"])
                            except json.JSONDecodeError:
                                args = {}
                            tool_call = {
                                "id": current_tool["id"],
                                "name": current_tool["name"],
                                "arguments": args,
                            }
                            tool_calls.append(tool_call)
                            yield {"type": "tool_call", "tool_call": tool_call}
                            current_tool = None
                    elif event.type == "message_stop":
                        pass

                # Get final message for usage
                final_message = await stream.get_final_message()
                yield {
                    "type": "done",
                    "content": full_content,
                    "tool_calls": tool_calls,
                    "usage": {
                        "prompt_tokens": final_message.usage.input_tokens,
                        "completion_tokens": final_message.usage.output_tokens,
                        "total_tokens": final_message.usage.input_tokens + final_message.usage.output_tokens,
                    },
                    "latency_ms": int((time.monotonic() - start) * 1000),
                }
        except Exception as e:
            logger.error(f"Claude streaming error: {e}")
            yield {"type": "error", "error": str(e)}
