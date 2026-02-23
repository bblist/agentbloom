"""
Tool: generate_page
Creates a new website page from a description. Uses the LLM to generate
structured content_blocks JSON that the page renderer will convert to HTML.
"""

import json
import logging
import uuid

from django.apps import apps
from django.utils import timezone
from django.utils.text import slugify

from . import register_tool

logger = logging.getLogger(__name__)

PAGE_BLOCK_TYPES = [
    "hero", "text", "image", "cta", "form", "pricing", "testimonials",
    "faq", "footer", "gallery", "features", "stats", "video", "contact",
    "team", "logo_cloud", "newsletter", "blog_feed",
]

GENERATE_PAGE_PROMPT = """Generate a complete website page as a JSON array of content blocks.

Each block must have:
- "type": one of {block_types}
- "id": a unique string ID
- "props": block-specific properties (see below)
- "styles": optional CSS overrides as key-value pairs

Block type schemas:
- hero: {{headline, subheadline, cta_text, cta_url, background_image, overlay_color, alignment}}
- text: {{heading, body, alignment}}
- image: {{src, alt, caption, width, aspect_ratio}}
- cta: {{headline, body, button_text, button_url, variant(primary|secondary|outline)}}
- form: {{title, description, fields: [{{name, type, label, required, placeholder}}], submit_text, success_message}}
- pricing: {{heading, tiers: [{{name, price, period, features: [], cta_text, highlighted}}]}}
- testimonials: {{heading, items: [{{quote, author, role, company, avatar_url, rating}}]}}
- faq: {{heading, items: [{{question, answer}}]}}
- footer: {{columns: [{{title, links: [{{text, url}}]}}], copyright, social_links: [{{platform, url}}]}}
- gallery: {{heading, images: [{{src, alt, caption}}], columns, layout(grid|masonry)}}
- features: {{heading, subheading, items: [{{icon, title, description}}], layout(grid|list)}}
- stats: {{heading, items: [{{value, label, description}}]}}
- video: {{url, title, thumbnail, autoplay}}
- contact: {{heading, email, phone, address, map_embed_url, form_fields}}
- team: {{heading, members: [{{name, role, bio, image_url, social}}]}}
- logo_cloud: {{heading, logos: [{{name, image_url, url}}]}}
- newsletter: {{heading, description, placeholder, button_text}}
- blog_feed: {{heading, count, show_excerpt, show_image}}

Generate content appropriate for: {description}
Business type: {business_type}
Page type: {page_type}

Return ONLY the JSON array of blocks, no markdown fencing."""


@register_tool(
    name="generate_page",
    description=(
        "Generate a new website page from a description. Creates structured content blocks "
        "that form the page layout and content. Specify what kind of page you want (e.g., "
        "'a landing page for an HVAC company' or 'an about page for a bakery')."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "What the page should be about and what it should convey.",
            },
            "page_type": {
                "type": "string",
                "enum": ["page", "landing", "blog_post", "legal", "utility"],
                "description": "Type of page to generate.",
                "default": "page",
            },
            "business_type": {
                "type": "string",
                "description": "The type of business (e.g., 'plumber', 'bakery', 'law firm').",
                "default": "",
            },
            "site_id": {
                "type": "string",
                "description": "UUID of the site to add the page to. If omitted, creates a standalone page draft.",
            },
            "title": {
                "type": "string",
                "description": "Page title. If omitted, the agent will generate one.",
            },
            "template_id": {
                "type": "string",
                "description": "Optional template UUID to base the page on.",
            },
        },
        "required": ["description"],
    },
)
async def generate_page(args: dict, context) -> dict:
    """Generate a page with AI-created content blocks."""
    from ..providers import get_provider

    description = args["description"]
    page_type = args.get("page_type", "page")
    business_type = args.get("business_type", "")
    site_id = args.get("site_id")
    title = args.get("title")
    template_id = args.get("template_id")

    config = context.agent_config

    # Use design provider for page generation
    provider = get_provider(
        provider_name=config.get("design_provider", "claude"),
        model=config.get("design_model", "claude-sonnet-4-20250514"),
        temperature=0.7,
        max_tokens=8192,
    )

    # Build the generation prompt
    prompt = GENERATE_PAGE_PROMPT.format(
        block_types=", ".join(PAGE_BLOCK_TYPES),
        description=description,
        business_type=business_type or "general business",
        page_type=page_type,
    )

    # If template, load it and include as reference
    if template_id:
        try:
            Template = apps.get_model("sites", "Template")
            template = await Template.objects.aget(id=template_id)
            prompt += f"\n\nBase your structure on this template:\n{json.dumps(template.blocks)}"
        except Exception:
            pass

    messages = [
        {"role": "system", "content": "You are a web design expert. Return only valid JSON arrays."},
        {"role": "user", "content": prompt},
    ]

    result = await provider.generate(messages)
    content_text = result.get("content", "[]")

    # Parse the JSON blocks
    try:
        # Strip potential markdown fencing
        if "```" in content_text:
            content_text = content_text.split("```")[1]
            if content_text.startswith("json"):
                content_text = content_text[4:]
        content_blocks = json.loads(content_text.strip())
    except json.JSONDecodeError:
        content_blocks = [
            {
                "type": "hero",
                "id": str(uuid.uuid4())[:8],
                "props": {
                    "headline": title or "Welcome",
                    "subheadline": description,
                    "cta_text": "Get Started",
                    "cta_url": "#contact",
                },
            },
            {
                "type": "text",
                "id": str(uuid.uuid4())[:8],
                "props": {
                    "heading": "About Us",
                    "body": description,
                },
            },
        ]

    # Generate title if not provided
    if not title:
        if content_blocks and content_blocks[0].get("props", {}).get("headline"):
            title = content_blocks[0]["props"]["headline"]
        else:
            title = description[:80]

    slug = slugify(title)[:200]

    # Save to database if site_id provided
    page_data = {
        "title": title,
        "slug": slug,
        "page_type": page_type,
        "content_blocks": content_blocks,
        "status": "draft",
    }

    if site_id:
        try:
            Site = apps.get_model("sites", "Site")
            Page = apps.get_model("sites", "Page")
            site = await Site.objects.aget(id=site_id, org_id=context.org_id)
            page = await Page.objects.acreate(
                site=site,
                title=title,
                slug=slug,
                path=f"/{slug}",
                page_type=page_type,
                content_blocks=content_blocks,
                status="draft",
            )
            page_data["page_id"] = str(page.id)
            page_data["site_id"] = str(site.id)
        except Exception as e:
            logger.warning(f"Could not save page to site: {e}")
            page_data["save_error"] = str(e)

    page_data["block_count"] = len(content_blocks)
    page_data["block_types_used"] = list({b["type"] for b in content_blocks})

    return page_data
