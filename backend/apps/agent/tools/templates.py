"""
Tool: manage_templates
List, select, and customize website templates.
"""

import json
import logging

from django.apps import apps

from . import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="list_templates",
    description=(
        "List available website templates. Optionally filter by category or industry. "
        "Returns template names, previews, and categories."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Filter by category (e.g., 'business', 'portfolio', 'ecommerce', 'blog').",
            },
            "industry": {
                "type": "string",
                "description": "Filter by industry (e.g., 'hvac', 'legal', 'restaurant').",
            },
        },
    },
)
async def list_templates(args: dict, context) -> dict:
    """List available templates."""
    Template = apps.get_model("sites", "Template")

    qs = Template.objects.filter(is_active=True)

    category = args.get("category")
    industry = args.get("industry")

    if category:
        qs = qs.filter(category__iexact=category)
    if industry:
        qs = qs.filter(industry__iexact=industry)

    templates = []
    async for t in qs[:20]:
        templates.append({
            "id": str(t.id),
            "name": t.name,
            "category": getattr(t, "category", ""),
            "industry": getattr(t, "industry", ""),
            "description": getattr(t, "description", ""),
            "preview_url": getattr(t, "preview_url", ""),
            "block_count": len(t.blocks) if hasattr(t, "blocks") and t.blocks else 0,
        })

    return {
        "templates": templates,
        "count": len(templates),
        "filters": {"category": category, "industry": industry},
    }


@register_tool(
    name="get_template",
    description="Get the full details and content blocks of a specific template.",
    parameters_schema={
        "type": "object",
        "properties": {
            "template_id": {
                "type": "string",
                "description": "UUID of the template.",
            },
        },
        "required": ["template_id"],
    },
)
async def get_template(args: dict, context) -> dict:
    """Get full template details."""
    Template = apps.get_model("sites", "Template")

    try:
        template = await Template.objects.aget(id=args["template_id"])
    except Template.DoesNotExist:
        return {"error": "Template not found.", "success": False}

    return {
        "id": str(template.id),
        "name": template.name,
        "category": getattr(template, "category", ""),
        "industry": getattr(template, "industry", ""),
        "description": getattr(template, "description", ""),
        "blocks": template.blocks if hasattr(template, "blocks") else [],
        "global_styles": template.global_styles if hasattr(template, "global_styles") else {},
    }


@register_tool(
    name="customize_template",
    description=(
        "Customize a template by applying business-specific content to its blocks. "
        "Uses AI to rewrite placeholder content with real business information."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "template_id": {
                "type": "string",
                "description": "UUID of the template to customize.",
            },
            "business_name": {
                "type": "string",
                "description": "Name of the business.",
            },
            "business_type": {
                "type": "string",
                "description": "Type of business (e.g., 'plumbing', 'bakery').",
            },
            "description": {
                "type": "string",
                "description": "Brief description of the business.",
            },
            "services": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of services offered.",
            },
            "location": {
                "type": "string",
                "description": "Business location.",
            },
            "phone": {
                "type": "string",
                "description": "Business phone number.",
            },
        },
        "required": ["template_id", "business_name"],
    },
)
async def customize_template(args: dict, context) -> dict:
    """Customize a template with business-specific content."""
    from ..providers import get_provider

    Template = apps.get_model("sites", "Template")

    try:
        template = await Template.objects.aget(id=args["template_id"])
    except Template.DoesNotExist:
        return {"error": "Template not found.", "success": False}

    config = context.agent_config
    provider = get_provider(
        provider_name=config.get("design_provider", "claude"),
        model=config.get("design_model", "claude-sonnet-4-20250514"),
        temperature=0.7,
        max_tokens=8192,
    )

    business_info = {
        "name": args["business_name"],
        "type": args.get("business_type", ""),
        "description": args.get("description", ""),
        "services": args.get("services", []),
        "location": args.get("location", ""),
        "phone": args.get("phone", ""),
    }

    blocks = template.blocks if hasattr(template, "blocks") else []

    messages = [
        {"role": "system", "content": (
            "You are a web design expert. Customize template content blocks by replacing "
            "placeholder content with real business information. Keep the structure and types "
            "identical, only change text content, headings, descriptions, and CTAs. "
            "Return the full JSON array of customized blocks."
        )},
        {"role": "user", "content": (
            f"Customize these template blocks for this business:\n\n"
            f"Business info: {json.dumps(business_info)}\n\n"
            f"Template blocks:\n{json.dumps(blocks)}\n\n"
            f"Return ONLY the customized JSON array."
        )},
    ]

    result = await provider.generate(messages)
    content = result.get("content", "[]")

    try:
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        customized_blocks = json.loads(content.strip())
    except json.JSONDecodeError:
        customized_blocks = blocks  # Fall back to original

    return {
        "template_id": str(template.id),
        "template_name": template.name,
        "customized_blocks": customized_blocks,
        "block_count": len(customized_blocks),
        "business_name": args["business_name"],
    }
