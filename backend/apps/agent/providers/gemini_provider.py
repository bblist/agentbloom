"""Google Gemini provider — design option, cost-efficient."""

import json
import logging
import time
from typing import AsyncIterator

from django.conf import settings

from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider (Gemini 3.2 Pro). Design-capable, cost-efficient."""

    provider_name = "gemini"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from google import genai
        self._genai = genai
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _format_tools_for_provider(self, tools: list | None):
        """Convert tool definitions to Gemini function declarations."""
        if not tools:
            return None
        declarations = []
        for t in tools:
            declarations.append(
                self._genai.types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=t["parameters"],
                )
            )
        return [self._genai.types.Tool(function_declarations=declarations)]

    def _convert_messages(self, messages: list) -> tuple[str, list]:
        """Convert messages to Gemini format."""
        system = ""
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system += msg["content"] + "\n"
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "tool":
                contents.append({
                    "role": "function",
                    "parts": [{"function_response": {
                        "name": msg.get("tool_name", ""),
                        "response": {"result": msg["content"]},
                    }}],
                })
        return system.strip(), contents

    async def generate(self, messages: list, tools: list | None = None) -> dict:
        self._log_request(messages, tools)
        start = time.monotonic()

        system_instruction, contents = self._convert_messages(messages)

        config = self._genai.types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        formatted_tools = self._format_tools_for_provider(tools)
        if formatted_tools:
            config.tools = formatted_tools

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

        latency_ms = int((time.monotonic() - start) * 1000)

        content = ""
        tool_calls = []
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    content += part.text
                elif hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    tool_calls.append({
                        "id": f"gemini_{fc.name}_{int(time.time())}",
                        "name": fc.name,
                        "arguments": dict(fc.args) if fc.args else {},
                    })

        usage_meta = response.usage_metadata if hasattr(response, "usage_metadata") else None
        usage = {
            "prompt_tokens": getattr(usage_meta, "prompt_token_count", 0) if usage_meta else 0,
            "completion_tokens": getattr(usage_meta, "candidates_token_count", 0) if usage_meta else 0,
            "total_tokens": getattr(usage_meta, "total_token_count", 0) if usage_meta else 0,
        }

        return {
            "content": content,
            "tool_calls": tool_calls,
            "usage": usage,
            "model": self.model,
            "latency_ms": latency_ms,
            "finish_reason": "stop",
        }

    async def stream(self, messages: list, tools: list | None = None) -> AsyncIterator[dict]:
        self._log_request(messages, tools)
        start = time.monotonic()

        system_instruction, contents = self._convert_messages(messages)

        config = self._genai.types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        formatted_tools = self._format_tools_for_provider(tools)
        if formatted_tools:
            config.tools = formatted_tools

        try:
            full_content = ""
            async for chunk in self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=config,
            ):
                if chunk.candidates:
                    for part in chunk.candidates[0].content.parts:
                        if hasattr(part, "text") and part.text:
                            full_content += part.text
                            yield {"type": "token", "content": part.text}
                        elif hasattr(part, "function_call") and part.function_call:
                            fc = part.function_call
                            yield {
                                "type": "tool_call",
                                "tool_call": {
                                    "id": f"gemini_{fc.name}_{int(time.time())}",
                                    "name": fc.name,
                                    "arguments": dict(fc.args) if fc.args else {},
                                },
                            }

            yield {
                "type": "done",
                "content": full_content,
                "latency_ms": int((time.monotonic() - start) * 1000),
            }
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            yield {"type": "error", "error": str(e)}
