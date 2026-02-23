"""
Tool: manage_site
Create, list, and manage sites for the organization.
"""

import logging

from django.apps import apps
from django.utils.text import slugify

from . import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="list_sites",
    description="List all websites belonging to the current organization.",
    parameters_schema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["draft", "published", "archived"],
                "description": "Filter by site status.",
            },
        },
    },
)
async def list_sites(args: dict, context) -> dict:
    """List org's sites."""
    Site = apps.get_model("sites", "Site")
    qs = Site.objects.filter(org_id=context.org_id)

    status = args.get("status")
    if status:
        qs = qs.filter(status=status)

    sites = []
    async for site in qs[:50]:
        page_count = await site.pages.acount()
        sites.append({
            "id": str(site.id),
            "name": site.name,
            "slug": site.slug,
            "status": site.status,
            "custom_domain": site.custom_domain,
            "page_count": page_count,
            "created_at": site.created_at.isoformat(),
        })

    return {"sites": sites, "count": len(sites)}


@register_tool(
    name="create_site",
    description=(
        "Create a new website. You can specify a name, template, and custom domain. "
        "This creates the site container — pages are added separately."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the website.",
            },
            "template_id": {
                "type": "string",
                "description": "Optional template UUID to apply.",
            },
            "custom_domain": {
                "type": "string",
                "description": "Custom domain (e.g., 'www.mybusiness.com').",
            },
            "global_styles": {
                "type": "object",
                "description": "Global style settings (colors, fonts, etc.).",
            },
        },
        "required": ["name"],
    },
)
async def create_site(args: dict, context) -> dict:
    """Create a new site."""
    Site = apps.get_model("sites", "Site")

    name = args["name"]
    slug = slugify(name)[:200]

    # Ensure unique slug
    base_slug = slug
    counter = 1
    while await Site.objects.filter(org_id=context.org_id, slug=slug).aexists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    site = await Site.objects.acreate(
        org_id=context.org_id,
        name=name,
        slug=slug,
        custom_domain=args.get("custom_domain", ""),
        global_styles=args.get("global_styles", {}),
        status="draft",
    )

    # Apply template if provided
    if args.get("template_id"):
        try:
            Template = apps.get_model("sites", "Template")
            template = await Template.objects.aget(id=args["template_id"])
            site.template = template
            if hasattr(template, "global_styles") and template.global_styles:
                site.global_styles = template.global_styles
            await site.asave()
        except Exception as e:
            logger.warning(f"Could not apply template: {e}")

    return {
        "site_id": str(site.id),
        "name": site.name,
        "slug": site.slug,
        "status": site.status,
        "custom_domain": site.custom_domain,
    }


@register_tool(
    name="list_pages",
    description="List all pages of a specific site.",
    parameters_schema={
        "type": "object",
        "properties": {
            "site_id": {
                "type": "string",
                "description": "UUID of the site.",
            },
        },
        "required": ["site_id"],
    },
)
async def list_pages(args: dict, context) -> dict:
    """List pages for a site."""
    Page = apps.get_model("sites", "Page")

    pages = []
    async for page in Page.objects.filter(
        site_id=args["site_id"],
        site__org_id=context.org_id,
    ).order_by("sort_order"):
        pages.append({
            "id": str(page.id),
            "title": page.title,
            "slug": page.slug,
            "path": page.path,
            "page_type": page.page_type,
            "status": page.status,
            "is_homepage": page.is_homepage,
            "block_count": len(page.content_blocks) if page.content_blocks else 0,
            "updated_at": page.updated_at.isoformat(),
        })

    return {"pages": pages, "count": len(pages), "site_id": args["site_id"]}


@register_tool(
    name="publish_site",
    description="Publish a draft site, making it live.",
    parameters_schema={
        "type": "object",
        "properties": {
            "site_id": {
                "type": "string",
                "description": "UUID of the site to publish.",
            },
        },
        "required": ["site_id"],
    },
)
async def publish_site(args: dict, context) -> dict:
    """Publish a site."""
    from django.utils import timezone

    Site = apps.get_model("sites", "Site")

    try:
        site = await Site.objects.aget(id=args["site_id"], org_id=context.org_id)
    except Site.DoesNotExist:
        return {"error": "Site not found.", "success": False}

    page_count = await site.pages.acount()
    if page_count == 0:
        return {"error": "Cannot publish a site with no pages.", "success": False}

    site.status = "published"
    site.published_at = timezone.now()
    await site.asave()

    return {
        "success": True,
        "site_id": str(site.id),
        "name": site.name,
        "status": "published",
        "page_count": page_count,
        "published_at": site.published_at.isoformat(),
    }
