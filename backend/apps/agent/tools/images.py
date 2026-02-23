"""
Tool: generate_images
Searches for stock images from Unsplash, or generates image descriptions
for AI image generation (Stable Diffusion, DALL-E, etc.)
"""

import logging
import httpx

from django.conf import settings

from . import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="search_images",
    description=(
        "Search for stock photos from Unsplash. Returns URLs and metadata for high-quality, "
        "free-to-use images. Use this when the user needs photos for their website pages."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for the image (e.g., 'modern kitchen renovation').",
            },
            "count": {
                "type": "integer",
                "description": "Number of images to return (1-10).",
                "default": 5,
            },
            "orientation": {
                "type": "string",
                "enum": ["landscape", "portrait", "squarish"],
                "description": "Image orientation.",
                "default": "landscape",
            },
        },
        "required": ["query"],
    },
)
async def search_images(args: dict, context) -> dict:
    """Search Unsplash for stock photos."""
    query = args["query"]
    count = min(args.get("count", 5), 10)
    orientation = args.get("orientation", "landscape")

    access_key = getattr(settings, "UNSPLASH_ACCESS_KEY", "")

    if not access_key:
        # Return placeholder images when no API key configured
        return {
            "images": [
                {
                    "url": f"https://images.unsplash.com/photo-placeholder-{i}?w=1200&q=80",
                    "thumb_url": f"https://images.unsplash.com/photo-placeholder-{i}?w=400&q=60",
                    "alt": f"{query} stock photo {i+1}",
                    "credit": "Unsplash",
                    "width": 1200,
                    "height": 800,
                }
                for i in range(count)
            ],
            "note": "Using placeholder URLs — set UNSPLASH_ACCESS_KEY for real images.",
            "query": query,
        }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.unsplash.com/search/photos",
                params={
                    "query": query,
                    "per_page": count,
                    "orientation": orientation,
                },
                headers={"Authorization": f"Client-ID {access_key}"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        images = []
        for photo in data.get("results", []):
            images.append({
                "url": photo["urls"]["regular"],
                "thumb_url": photo["urls"]["thumb"],
                "full_url": photo["urls"]["full"],
                "alt": photo.get("alt_description", query),
                "credit": photo["user"]["name"],
                "credit_url": photo["user"]["links"]["html"],
                "width": photo["width"],
                "height": photo["height"],
                "color": photo.get("color", "#000"),
                "unsplash_id": photo["id"],
            })

        return {
            "images": images,
            "total": data.get("total", 0),
            "query": query,
        }
    except Exception as e:
        logger.warning(f"Unsplash search failed: {e}")
        return {
            "images": [],
            "error": str(e),
            "query": query,
        }


@register_tool(
    name="generate_image_prompt",
    description=(
        "Generate a detailed AI image generation prompt for creating custom images. "
        "Returns a prompt suitable for Stable Diffusion, DALL-E, or Midjourney."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "What the image should depict.",
            },
            "style": {
                "type": "string",
                "enum": [
                    "photo-realistic", "illustration", "flat-design", "3d-render",
                    "watercolor", "minimalist", "vintage", "corporate", "hand-drawn",
                ],
                "description": "Visual style for the image.",
                "default": "photo-realistic",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["16:9", "4:3", "1:1", "9:16", "3:2"],
                "description": "Image aspect ratio.",
                "default": "16:9",
            },
        },
        "required": ["description"],
    },
)
async def generate_image_prompt(args: dict, context) -> dict:
    """Generate a detailed image generation prompt."""
    from ..providers import get_provider

    description = args["description"]
    style = args.get("style", "photo-realistic")
    aspect_ratio = args.get("aspect_ratio", "16:9")

    config = context.agent_config
    provider = get_provider(
        provider_name=config.get("design_provider", "claude"),
        model=config.get("design_model", "claude-sonnet-4-20250514"),
        temperature=0.9,
        max_tokens=1024,
    )

    messages = [
        {"role": "system", "content": (
            "You are an expert at writing detailed image generation prompts. "
            "Create a detailed, descriptive prompt optimized for AI image generation. "
            "Include: subject, composition, lighting, mood, color palette, style details. "
            "Return ONLY the prompt text."
        )},
        {"role": "user", "content": (
            f"Create an image generation prompt for: {description}\n"
            f"Style: {style}\nAspect ratio: {aspect_ratio}"
        )},
    ]

    result = await provider.generate(messages)
    prompt_text = result.get("content", description).strip()

    return {
        "prompt": prompt_text,
        "style": style,
        "aspect_ratio": aspect_ratio,
        "description": description,
    }
