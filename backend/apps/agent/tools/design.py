"""
Tool: design_styles
Generate color palettes, font pairings, and global site styles using AI.
"""

import json
import logging

from . import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="generate_color_palette",
    description=(
        "Generate a cohesive color palette for a website based on industry, mood, or preferences. "
        "Returns primary, secondary, accent, background, and text colors."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "industry": {
                "type": "string",
                "description": "Business industry (e.g., 'healthcare', 'technology', 'restaurant').",
            },
            "mood": {
                "type": "string",
                "enum": ["professional", "modern", "playful", "elegant", "bold", "warm", "cool", "natural"],
                "description": "Desired mood/feel.",
                "default": "professional",
            },
            "base_color": {
                "type": "string",
                "description": "Optional hex color to build palette around (e.g., '#2563EB').",
            },
        },
        "required": ["industry"],
    },
)
async def generate_color_palette(args: dict, context) -> dict:
    """Generate a color palette using AI."""
    from ..providers import get_provider

    config = context.agent_config
    provider = get_provider(
        provider_name=config.get("design_provider", "claude"),
        model=config.get("design_model", "claude-sonnet-4-20250514"),
        temperature=0.8,
        max_tokens=1024,
    )

    prompt_parts = [
        f"Generate a professional website color palette for a {args['industry']} business.",
        f"Mood: {args.get('mood', 'professional')}",
    ]
    if args.get("base_color"):
        prompt_parts.append(f"Build around this base color: {args['base_color']}")

    prompt_parts.append(
        "\nReturn as JSON with these keys:\n"
        '{"primary": "#hex", "secondary": "#hex", "accent": "#hex", '
        '"background": "#hex", "surface": "#hex", "text": "#hex", '
        '"text_light": "#hex", "border": "#hex", "error": "#hex", "success": "#hex"}\n'
        "Return ONLY the JSON object."
    )

    messages = [
        {"role": "system", "content": "You are a color theory expert. Return only valid JSON."},
        {"role": "user", "content": "\n".join(prompt_parts)},
    ]

    result = await provider.generate(messages)
    content = result.get("content", "{}")

    try:
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        palette = json.loads(content.strip())
    except json.JSONDecodeError:
        palette = {
            "primary": "#2563EB",
            "secondary": "#7C3AED",
            "accent": "#F59E0B",
            "background": "#FFFFFF",
            "surface": "#F8FAFC",
            "text": "#1E293B",
            "text_light": "#64748B",
            "border": "#E2E8F0",
            "error": "#EF4444",
            "success": "#22C55E",
        }

    return {
        "palette": palette,
        "industry": args["industry"],
        "mood": args.get("mood", "professional"),
    }


@register_tool(
    name="generate_font_pairing",
    description=(
        "Generate a font pairing — heading and body fonts that work well together. "
        "Returns Google Fonts names and CSS import URLs."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "style": {
                "type": "string",
                "enum": ["modern", "classic", "playful", "elegant", "minimal", "bold"],
                "description": "Typography style.",
                "default": "modern",
            },
            "industry": {
                "type": "string",
                "description": "Business industry for context.",
            },
        },
    },
)
async def generate_font_pairing(args: dict, context) -> dict:
    """Generate font pairing recommendation."""
    # Curated font pairings (no LLM call needed)
    pairings = {
        "modern": {"heading": "Inter", "body": "Inter", "accent": "JetBrains Mono"},
        "classic": {"heading": "Playfair Display", "body": "Source Serif 4", "accent": "Cormorant Garamond"},
        "playful": {"heading": "Fredoka One", "body": "Nunito", "accent": "Caveat"},
        "elegant": {"heading": "Cormorant Garamond", "body": "Lato", "accent": "Playfair Display"},
        "minimal": {"heading": "DM Sans", "body": "DM Sans", "accent": "Space Mono"},
        "bold": {"heading": "Montserrat", "body": "Open Sans", "accent": "Bebas Neue"},
    }

    style = args.get("style", "modern")
    fonts = pairings.get(style, pairings["modern"])

    # Build Google Fonts URL
    font_families = set(fonts.values())
    params = "|".join(f.replace(" ", "+") for f in font_families)
    google_fonts_url = f"https://fonts.googleapis.com/css2?family={params}&display=swap"

    return {
        "fonts": fonts,
        "style": style,
        "google_fonts_url": google_fonts_url,
        "css_variables": {
            "--font-heading": f"'{fonts['heading']}', sans-serif",
            "--font-body": f"'{fonts['body']}', sans-serif",
            "--font-accent": f"'{fonts['accent']}', monospace",
        },
    }


@register_tool(
    name="generate_global_styles",
    description=(
        "Generate complete global styles for a site — colors, fonts, spacing, border radius, "
        "shadows, and responsive breakpoints. Combines palette + fonts into a cohesive design system."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "industry": {
                "type": "string",
                "description": "Business industry.",
            },
            "mood": {
                "type": "string",
                "enum": ["professional", "modern", "playful", "elegant", "bold", "warm", "cool"],
                "default": "professional",
            },
            "base_color": {
                "type": "string",
                "description": "Optional hex color to build around.",
            },
            "site_id": {
                "type": "string",
                "description": "Optional site UUID to apply styles to.",
            },
        },
        "required": ["industry"],
    },
)
async def generate_global_styles(args: dict, context) -> dict:
    """Generate and optionally apply global styles."""
    from django.apps import apps

    # Generate palette
    palette_result = await generate_color_palette(args, context)
    palette = palette_result["palette"]

    # Generate fonts
    font_result = await generate_font_pairing(
        {"style": args.get("mood", "modern"), "industry": args.get("industry")},
        context,
    )
    fonts = font_result["fonts"]

    global_styles = {
        "colors": palette,
        "fonts": fonts,
        "google_fonts_url": font_result["google_fonts_url"],
        "spacing": {
            "xs": "0.25rem",
            "sm": "0.5rem",
            "md": "1rem",
            "lg": "1.5rem",
            "xl": "2rem",
            "2xl": "3rem",
            "3xl": "4rem",
        },
        "border_radius": {
            "sm": "0.25rem",
            "md": "0.5rem",
            "lg": "0.75rem",
            "xl": "1rem",
            "full": "9999px",
        },
        "shadows": {
            "sm": "0 1px 2px 0 rgba(0,0,0,0.05)",
            "md": "0 4px 6px -1px rgba(0,0,0,0.1)",
            "lg": "0 10px 15px -3px rgba(0,0,0,0.1)",
            "xl": "0 20px 25px -5px rgba(0,0,0,0.1)",
        },
        "max_width": "1280px",
    }

    # Apply to site if provided
    if args.get("site_id"):
        try:
            Site = apps.get_model("sites", "Site")
            site = await Site.objects.aget(id=args["site_id"], org_id=context.org_id)
            site.global_styles = global_styles
            await site.asave()
            return {
                "styles": global_styles,
                "applied_to_site": str(site.id),
                "site_name": site.name,
            }
        except Exception as e:
            logger.warning(f"Could not apply styles to site: {e}")

    return {"styles": global_styles}
