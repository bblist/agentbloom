"""
Tool: generate_copy
Writes editorial copy — headlines, body text, CTAs, blog posts, bios, taglines, etc.
"""

import json
import logging

from . import register_tool

logger = logging.getLogger(__name__)

COPY_TYPES = {
    "headline": "Write a compelling headline",
    "tagline": "Write a short, memorable tagline",
    "body": "Write clear, engaging body copy",
    "cta": "Write a persuasive call-to-action",
    "blog_post": "Write a full blog post with headings and paragraphs",
    "bio": "Write a professional bio",
    "product_description": "Write a product or service description",
    "email_subject": "Write an email subject line",
    "email_body": "Write an email body",
    "social_post": "Write a social media post",
    "faq_answer": "Write a clear FAQ answer",
    "testimonial": "Write a realistic testimonial",
    "meta_description": "Write an SEO meta description (max 160 chars)",
}


@register_tool(
    name="generate_copy",
    description=(
        "Write professional copy for any purpose — headlines, body text, CTAs, blog posts, "
        "product descriptions, email content, social posts, bios, taglines, and more. "
        "Specify the type, topic, and tone."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "copy_type": {
                "type": "string",
                "enum": list(COPY_TYPES.keys()),
                "description": "Type of copy to generate.",
            },
            "topic": {
                "type": "string",
                "description": "What the copy should be about.",
            },
            "tone": {
                "type": "string",
                "enum": ["professional", "friendly", "casual", "formal", "playful", "urgent", "empathetic"],
                "description": "Tone of voice for the copy.",
                "default": "professional",
            },
            "audience": {
                "type": "string",
                "description": "Target audience (e.g., 'homeowners', 'small business owners').",
                "default": "",
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "SEO keywords to include naturally.",
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum character count for the copy.",
            },
            "variations": {
                "type": "integer",
                "description": "Number of variations to generate (1-5).",
                "default": 1,
            },
            "context": {
                "type": "string",
                "description": "Additional context about the business/product.",
            },
        },
        "required": ["copy_type", "topic"],
    },
)
async def generate_copy(args: dict, context) -> dict:
    """Generate copy using the LLM."""
    from ..providers import get_provider

    copy_type = args["copy_type"]
    topic = args["topic"]
    tone = args.get("tone", "professional")
    audience = args.get("audience", "")
    keywords = args.get("keywords", [])
    max_length = args.get("max_length")
    variations = min(args.get("variations", 1), 5)
    extra_context = args.get("context", "")

    config = context.agent_config

    provider = get_provider(
        provider_name=config.get("llm_provider", "openai"),
        model=config.get("llm_model", "gpt-4o"),
        temperature=0.8,
        max_tokens=4096,
    )

    instruction = COPY_TYPES.get(copy_type, "Write copy")

    prompt_parts = [
        f"{instruction} about: {topic}",
        f"Tone: {tone}",
    ]

    if audience:
        prompt_parts.append(f"Target audience: {audience}")
    if keywords:
        prompt_parts.append(f"Include these keywords naturally: {', '.join(keywords)}")
    if max_length:
        prompt_parts.append(f"Maximum length: {max_length} characters")
    if extra_context:
        prompt_parts.append(f"Additional context: {extra_context}")

    if variations > 1:
        prompt_parts.append(
            f"\nGenerate {variations} distinct variations. "
            f"Return as a JSON array of strings: [\"variation1\", \"variation2\", ...]"
        )
        prompt_parts.append("Return ONLY the JSON array.")
    else:
        prompt_parts.append("\nReturn ONLY the copy text, no quotes or formatting.")

    messages = [
        {"role": "system", "content": "You are an expert copywriter. Write compelling, conversion-focused copy."},
        {"role": "user", "content": "\n".join(prompt_parts)},
    ]

    result = await provider.generate(messages)
    content = result.get("content", "").strip()

    if variations > 1:
        try:
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            parsed = json.loads(content.strip())
            return {
                "copy_type": copy_type,
                "variations": parsed if isinstance(parsed, list) else [parsed],
                "count": len(parsed) if isinstance(parsed, list) else 1,
            }
        except json.JSONDecodeError:
            return {
                "copy_type": copy_type,
                "variations": [content],
                "count": 1,
            }
    else:
        # Strip surrounding quotes if present
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        return {
            "copy_type": copy_type,
            "text": content,
            "character_count": len(content),
        }
