"""
Tool: knowledge_base
Search the organization's knowledge base for relevant context.
"""

import logging

from django.apps import apps
from django.db.models import Q

from . import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="search_knowledge_base",
    description=(
        "Search the organization's knowledge base for information about the business. "
        "Use this to find details about services, products, policies, FAQs, etc. "
        "when you need business-specific context to answer questions or generate content."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query — what information are you looking for?",
            },
            "category": {
                "type": "string",
                "description": "Optional category filter (e.g., 'services', 'faq', 'about', 'products').",
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return.",
                "default": 5,
            },
        },
        "required": ["query"],
    },
)
async def search_knowledge_base(args: dict, context) -> dict:
    """Search the knowledge base using text matching (vector search when pgvector configured)."""
    KBEntry = apps.get_model("knowledge_base", "KBEntry")

    query = args["query"]
    category = args.get("category")
    limit = min(args.get("limit", 5), 20)

    # Text-based search (can be upgraded to vector search with pgvector)
    qs = KBEntry.objects.filter(
        org_id=context.org_id,
        is_active=True,
    ).filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(tags__contains=[query])
    )

    if category:
        qs = qs.filter(category__iexact=category)

    results = []
    async for entry in qs[:limit]:
        results.append({
            "id": str(entry.id),
            "title": entry.title,
            "content": entry.content[:500],
            "category": getattr(entry, "category", ""),
            "tags": entry.tags if hasattr(entry, "tags") else [],
            "source": getattr(entry, "source", ""),
            "relevance": "text_match",
        })

    # Also search KB FAQs
    try:
        KBFaq = apps.get_model("knowledge_base", "KBFaq")
        faq_qs = KBFaq.objects.filter(
            org_id=context.org_id,
        ).filter(
            Q(question__icontains=query) |
            Q(answer__icontains=query)
        )

        async for faq in faq_qs[:3]:
            results.append({
                "id": str(faq.id),
                "title": faq.question,
                "content": faq.answer[:500],
                "category": "faq",
                "tags": [],
                "source": "faq",
                "relevance": "text_match",
            })
    except Exception:
        pass  # KBFaq might not exist yet

    return {
        "results": results,
        "count": len(results),
        "query": query,
    }


@register_tool(
    name="get_business_info",
    description=(
        "Get the organization's business information — name, type, location, services, contact details. "
        "Useful as context before generating any business-specific content."
    ),
    parameters_schema={
        "type": "object",
        "properties": {},
    },
)
async def get_business_info(args: dict, context) -> dict:
    """Get business info from the org profile."""
    Organization = apps.get_model("users", "Organization")

    try:
        org = await Organization.objects.aget(id=context.org_id)
    except Organization.DoesNotExist:
        return {"error": "Organization not found.", "success": False}

    info = {
        "name": org.name,
        "slug": org.slug,
    }

    # Pull from org metadata if available
    if hasattr(org, "metadata") and org.metadata:
        meta = org.metadata
        info.update({
            "business_type": meta.get("business_type", ""),
            "industry": meta.get("industry", ""),
            "location": meta.get("location", ""),
            "phone": meta.get("phone", ""),
            "email": meta.get("email", ""),
            "website": meta.get("website", ""),
            "services": meta.get("services", []),
            "description": meta.get("description", ""),
            "service_area": meta.get("service_area", ""),
        })

    # Check for KB entries about the business
    try:
        KBEntry = apps.get_model("knowledge_base", "KBEntry")
        about_entries = []
        async for entry in KBEntry.objects.filter(
            org_id=context.org_id,
            is_active=True,
            category__in=["about", "services", "general"],
        )[:5]:
            about_entries.append({
                "title": entry.title,
                "content": entry.content[:300],
            })
        if about_entries:
            info["knowledge_base_entries"] = about_entries
    except Exception:
        pass

    return info
