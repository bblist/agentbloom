"""
AgentBloom ReAct Agent Engine

Custom ReAct-style reasoning loop:
  Input → Reason → Act → Observe → Loop

The agent receives user input, reasons about what to do, selects and executes tools,
observes the results, and either responds or continues reasoning.
"""

import json
import logging
import time
import hashlib
from typing import AsyncIterator
from dataclasses import dataclass, field

from django.conf import settings
from django.utils import timezone

from .providers import get_provider, BaseLLMProvider
from .tools import get_available_tools, TOOL_REGISTRY

logger = logging.getLogger(__name__)

MAX_REASONING_STEPS = 10  # Prevent infinite loops
MAX_TOOL_CALLS_PER_STEP = 3


@dataclass
class AgentContext:
    """Context for a single agent invocation."""
    org_id: str
    user_id: str
    conversation_id: str
    agent_config: dict
    knowledge_context: str = ""
    learnings: list = field(default_factory=list)
    debug: bool = False


@dataclass
class AgentResult:
    """Result from the agent engine."""
    content: str
    tool_calls_made: list = field(default_factory=list)
    total_tokens: int = 0
    model_used: str = ""
    latency_ms: int = 0
    confidence: float = 1.0
    reasoning_steps: list = field(default_factory=list)


def build_system_prompt(config: dict, knowledge_context: str = "", learnings: list = None) -> str:
    """Build the system prompt from agent config, KB context, and learnings."""
    tone_map = {
        "professional": "Maintain a professional, competent tone.",
        "friendly": "Be warm, friendly, and approachable.",
        "casual": "Keep it casual and conversational.",
        "formal": "Use formal, polished language.",
    }

    parts = [
        config.get("persona", "You are a helpful business assistant."),
        "",
        tone_map.get(config.get("tone", "friendly"), ""),
        "",
        "You are AgentBloom, an AI-powered business assistant. You help users build websites, "
        "manage their online business, send emails, create courses, handle bookings, and more.",
        "",
        "CAPABILITIES:",
        "- Generate and edit website pages (content, layout, styling)",
        "- Write copy (headlines, descriptions, CTAs, blog posts)",
        "- Search for stock images",
        "- Manage templates and components",
        "- Answer questions about the user's business using their knowledge base",
        "",
        "GUIDELINES:",
        "- Always explain what you're about to do before doing it",
        "- Ask for clarification when the request is ambiguous",
        "- After generating content, ask if the user wants to review or edit",
        "- Be concise but thorough",
        "- When showing generated content, format it nicely with markdown",
    ]

    if knowledge_context:
        parts.extend([
            "",
            "BUSINESS KNOWLEDGE (from the user's knowledge base):",
            knowledge_context,
        ])

    if learnings:
        parts.extend([
            "",
            "USER PREFERENCES (learned from previous corrections):",
        ])
        for l in learnings[:10]:  # Limit to last 10
            parts.append(f"- {l['category']}: {l['corrected_output'][:200]}")

    return "\n".join(parts)


def build_messages(system_prompt: str, conversation_messages: list) -> list:
    """Build the LLM message list from system prompt + conversation history."""
    messages = [{"role": "system", "content": system_prompt}]

    for msg in conversation_messages:
        if msg.get("is_undone"):
            continue
        role = msg["role"]
        if role == "tool":
            messages.append({
                "role": "tool",
                "content": json.dumps(msg.get("tool_result", {})),
                "tool_call_id": msg.get("tool_call_id", ""),
                "tool_name": msg.get("tool_name", ""),
            })
        else:
            messages.append({
                "role": role,
                "content": msg["content"],
            })

    return messages


def get_tool_definitions(org) -> list:
    """Get tool definitions in the format expected by LLM providers."""
    available = get_available_tools(org)
    definitions = []
    for name, tool in available.items():
        definitions.append({
            "name": name,
            "description": tool["description"],
            "parameters": tool["parameters"],
        })
    return definitions


async def execute_tool(tool_name: str, arguments: dict, context: AgentContext) -> dict:
    """Execute a registered tool and return the result."""
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        return {"error": f"Unknown tool: {tool_name}", "success": False}

    handler = tool["handler"]
    try:
        result = await handler(arguments, context)
        return {"result": result, "success": True}
    except Exception as e:
        logger.error(f"Tool execution error ({tool_name}): {e}")
        return {"error": str(e), "success": False}


def _get_provider_with_fallback(config: dict) -> BaseLLMProvider:
    """Get the primary provider, with fallback info ready."""
    return get_provider(
        provider_name=config.get("llm_provider", settings.DEFAULT_LLM_PROVIDER),
        model=config.get("llm_model", settings.DEFAULT_LLM_MODEL),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
    )


def _get_fallback_provider(config: dict) -> BaseLLMProvider:
    """Get the fallback provider."""
    return get_provider(
        provider_name=config.get("fallback_provider", settings.FALLBACK_LLM_PROVIDER),
        model=config.get("fallback_model", settings.FALLBACK_LLM_MODEL),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
    )


async def run_agent(
    user_message: str,
    conversation_messages: list,
    context: AgentContext,
    org=None,
) -> AgentResult:
    """
    Run the ReAct agent loop (non-streaming).

    1. Build system prompt + conversation context
    2. Send to LLM with tool definitions
    3. If LLM returns tool calls → execute tools → feed results back → loop
    4. If LLM returns text → return as final response
    """
    config = context.agent_config
    system_prompt = build_system_prompt(config, context.knowledge_context, context.learnings)
    messages = build_messages(system_prompt, conversation_messages)
    messages.append({"role": "user", "content": user_message})

    tool_defs = get_tool_definitions(org) if org else []
    provider = _get_provider_with_fallback(config)

    total_tokens = 0
    tool_calls_made = []
    reasoning_steps = []
    model_used = config.get("llm_model", settings.DEFAULT_LLM_MODEL)
    start = time.monotonic()

    for step in range(MAX_REASONING_STEPS):
        try:
            result = await provider.generate(messages, tools=tool_defs if tool_defs else None)
        except Exception as e:
            logger.warning(f"Primary LLM failed, trying fallback: {e}")
            try:
                provider = _get_fallback_provider(config)
                model_used = config.get("fallback_model", settings.FALLBACK_LLM_MODEL)
                result = await provider.generate(messages, tools=tool_defs if tool_defs else None)
            except Exception as e2:
                logger.error(f"Fallback LLM also failed: {e2}")
                return AgentResult(
                    content="I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                    total_tokens=total_tokens,
                    model_used=model_used,
                    latency_ms=int((time.monotonic() - start) * 1000),
                )

        total_tokens += result.get("usage", {}).get("total_tokens", 0)
        model_used = result.get("model", model_used)

        reasoning_steps.append({
            "step": step + 1,
            "content": result["content"][:200] if result["content"] else "",
            "tool_calls": [tc["name"] for tc in result.get("tool_calls", [])],
        })

        # If no tool calls, we have the final response
        if not result.get("tool_calls"):
            return AgentResult(
                content=result["content"],
                tool_calls_made=tool_calls_made,
                total_tokens=total_tokens,
                model_used=model_used,
                latency_ms=int((time.monotonic() - start) * 1000),
                reasoning_steps=reasoning_steps,
            )

        # Execute tool calls
        if result["content"]:
            messages.append({"role": "assistant", "content": result["content"]})

        for tc in result["tool_calls"][:MAX_TOOL_CALLS_PER_STEP]:
            tool_result = await execute_tool(tc["name"], tc["arguments"], context)
            tool_calls_made.append({
                "name": tc["name"],
                "arguments": tc["arguments"],
                "result": tool_result,
            })

            # Add tool result to messages for next iteration
            messages.append({
                "role": "tool",
                "content": json.dumps(tool_result),
                "tool_call_id": tc.get("id", ""),
                "tool_name": tc["name"],
            })

    # Max steps reached
    return AgentResult(
        content="I've been working on your request but it's taking longer than expected. Here's what I've done so far. Could you help me narrow down what you need?",
        tool_calls_made=tool_calls_made,
        total_tokens=total_tokens,
        model_used=model_used,
        latency_ms=int((time.monotonic() - start) * 1000),
        reasoning_steps=reasoning_steps,
    )


async def run_agent_streaming(
    user_message: str,
    conversation_messages: list,
    context: AgentContext,
    org=None,
) -> AsyncIterator[dict]:
    """
    Run the ReAct agent loop with streaming output.

    Yields events:
      - {"type": "thinking", "content": "..."} — agent reasoning
      - {"type": "token", "content": "..."} — response token
      - {"type": "tool_start", "tool": "...", "args": {...}}
      - {"type": "tool_result", "tool": "...", "result": {...}}
      - {"type": "done", "usage": {...}, "message_id": "..."}
      - {"type": "error", "error": "..."}
    """
    config = context.agent_config
    system_prompt = build_system_prompt(config, context.knowledge_context, context.learnings)
    messages = build_messages(system_prompt, conversation_messages)
    messages.append({"role": "user", "content": user_message})

    tool_defs = get_tool_definitions(org) if org else []
    provider = _get_provider_with_fallback(config)
    total_tokens = 0

    for step in range(MAX_REASONING_STEPS):
        full_content = ""
        tool_calls = []

        try:
            async for event in provider.stream(messages, tools=tool_defs if tool_defs else None):
                if event["type"] == "token":
                    full_content += event["content"]
                    yield event
                elif event["type"] == "tool_call":
                    tool_calls.append(event["tool_call"])
                elif event["type"] == "done":
                    total_tokens += event.get("usage", {}).get("total_tokens", 0)
                    if event.get("tool_calls"):
                        tool_calls.extend(event["tool_calls"])
                elif event["type"] == "error":
                    # Try fallback
                    logger.warning(f"Primary LLM stream error, trying fallback: {event['error']}")
                    provider = _get_fallback_provider(config)
                    break  # Will retry in next loop iteration
        except Exception as e:
            logger.warning(f"Primary LLM stream failed, trying fallback: {e}")
            provider = _get_fallback_provider(config)
            continue

        # No tool calls → done
        if not tool_calls:
            yield {
                "type": "done",
                "content": full_content,
                "usage": {"total_tokens": total_tokens},
            }
            return

        # Execute tool calls
        if full_content:
            messages.append({"role": "assistant", "content": full_content})

        for tc in tool_calls[:MAX_TOOL_CALLS_PER_STEP]:
            yield {"type": "tool_start", "tool": tc["name"], "args": tc["arguments"]}

            tool_result = await execute_tool(tc["name"], tc["arguments"], context)

            yield {"type": "tool_result", "tool": tc["name"], "result": tool_result}

            messages.append({
                "role": "tool",
                "content": json.dumps(tool_result),
                "tool_call_id": tc.get("id", ""),
                "tool_name": tc["name"],
            })

    yield {
        "type": "done",
        "content": "",
        "usage": {"total_tokens": total_tokens},
    }
