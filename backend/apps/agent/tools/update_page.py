"""
Tool: update_page
Updates an existing page's content blocks, either fully or partially.
Supports updating specific blocks by ID, adding new blocks, or removing blocks.
"""

import json
import logging

from django.apps import apps

from . import register_tool

logger = logging.getLogger(__name__)


@register_tool(
    name="update_page",
    description=(
        "Update an existing website page. You can replace the entire content, "
        "update specific blocks, add new blocks, remove blocks, or change page metadata "
        "like title, SEO fields, or styles."
    ),
    parameters_schema={
        "type": "object",
        "properties": {
            "page_id": {
                "type": "string",
                "description": "UUID of the page to update.",
            },
            "updates": {
                "type": "object",
                "description": "Fields to update on the page (title, slug, seo_title, seo_description, custom_css, etc.).",
            },
            "replace_blocks": {
                "type": "array",
                "description": "Full replacement of content_blocks array.",
            },
            "update_blocks": {
                "type": "array",
                "description": "Partial updates: [{id: 'block_id', props: {...new_props}}]. Merges with existing block props.",
            },
            "add_blocks": {
                "type": "array",
                "description": "New blocks to append to the page: [{type, props, styles}].",
            },
            "remove_block_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Block IDs to remove from the page.",
            },
            "insert_block": {
                "type": "object",
                "description": "Insert a block at a specific position: {index: number, block: {type, props}}.",
            },
        },
        "required": ["page_id"],
    },
)
async def update_page(args: dict, context) -> dict:
    """Update a page with the specified changes."""
    Page = apps.get_model("sites", "Page")
    PageVersion = apps.get_model("sites", "PageVersion")

    page_id = args["page_id"]

    try:
        page = await Page.objects.select_related("site").aget(
            id=page_id, site__org_id=context.org_id
        )
    except Page.DoesNotExist:
        return {"error": f"Page {page_id} not found.", "success": False}

    # Save version before modifying
    version_count = await PageVersion.objects.filter(page=page).acount()
    await PageVersion.objects.acreate(
        page=page,
        version_number=version_count + 1,
        content_blocks=page.content_blocks,
        diff_summary=f"Auto-saved before agent update",
    )

    blocks = list(page.content_blocks)
    changes_made = []

    # Full block replacement
    if "replace_blocks" in args:
        blocks = args["replace_blocks"]
        changes_made.append(f"Replaced all blocks ({len(blocks)} total)")

    # Update specific blocks by ID
    if "update_blocks" in args:
        for update in args["update_blocks"]:
            block_id = update.get("id")
            for i, block in enumerate(blocks):
                if block.get("id") == block_id:
                    if "props" in update:
                        block.setdefault("props", {}).update(update["props"])
                    if "styles" in update:
                        block.setdefault("styles", {}).update(update["styles"])
                    if "type" in update:
                        block["type"] = update["type"]
                    blocks[i] = block
                    changes_made.append(f"Updated block '{block_id}'")
                    break

    # Remove blocks by ID
    if "remove_block_ids" in args:
        remove_ids = set(args["remove_block_ids"])
        original_count = len(blocks)
        blocks = [b for b in blocks if b.get("id") not in remove_ids]
        changes_made.append(f"Removed {original_count - len(blocks)} block(s)")

    # Insert block at position
    if "insert_block" in args:
        insert = args["insert_block"]
        idx = insert.get("index", len(blocks))
        block = insert.get("block", {})
        if not block.get("id"):
            import uuid
            block["id"] = str(uuid.uuid4())[:8]
        blocks.insert(idx, block)
        changes_made.append(f"Inserted '{block.get('type', 'unknown')}' block at position {idx}")

    # Add blocks at end
    if "add_blocks" in args:
        for block in args["add_blocks"]:
            if not block.get("id"):
                import uuid
                block["id"] = str(uuid.uuid4())[:8]
            blocks.append(block)
        changes_made.append(f"Added {len(args['add_blocks'])} new block(s)")

    page.content_blocks = blocks

    # Update metadata fields
    if "updates" in args:
        for field, value in args["updates"].items():
            if hasattr(page, field) and field not in ("id", "site", "created_at"):
                setattr(page, field, value)
                changes_made.append(f"Updated {field}")

    await page.asave()

    return {
        "success": True,
        "page_id": str(page.id),
        "title": page.title,
        "block_count": len(blocks),
        "changes": changes_made,
        "version_saved": version_count + 1,
    }
