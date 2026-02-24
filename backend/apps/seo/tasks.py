"""Celery tasks for SEO processing."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_seo_audit(site_id):
    """Run a full SEO audit on a site's pages."""
    from apps.sites.models import Site, Page
    from .models import SEOAudit

    try:
        site = Site.objects.get(id=site_id)
        pages = Page.objects.filter(site=site)
        issues = []

        for page in pages:
            meta = page.seo_metadata or {}
            content_blocks = page.content_blocks or []

            # Check meta title
            title = meta.get("title", "")
            if not title:
                issues.append({
                    "page": str(page.id),
                    "slug": page.slug,
                    "type": "missing_title",
                    "severity": "high",
                    "message": f"Page '{page.title}' is missing a meta title",
                })
            elif len(title) > 60:
                issues.append({
                    "page": str(page.id),
                    "slug": page.slug,
                    "type": "title_too_long",
                    "severity": "medium",
                    "message": f"Meta title is {len(title)} chars (max 60)",
                })

            # Check meta description
            desc = meta.get("description", "")
            if not desc:
                issues.append({
                    "page": str(page.id),
                    "slug": page.slug,
                    "type": "missing_description",
                    "severity": "high",
                    "message": f"Page '{page.title}' is missing a meta description",
                })
            elif len(desc) > 160:
                issues.append({
                    "page": str(page.id),
                    "slug": page.slug,
                    "type": "description_too_long",
                    "severity": "low",
                    "message": f"Meta description is {len(desc)} chars (max 160)",
                })

            # Check for H1
            has_h1 = False
            for block in content_blocks:
                if block.get("type") == "hero":
                    has_h1 = True
                    break
                if block.get("type") == "text":
                    content = block.get("content", "")
                    if "<h1" in content.lower() or block.get("tag") == "h1":
                        has_h1 = True
                        break
            if not has_h1:
                issues.append({
                    "page": str(page.id),
                    "slug": page.slug,
                    "type": "missing_h1",
                    "severity": "medium",
                    "message": f"Page '{page.title}' may be missing an H1 heading",
                })

            # Check images for alt text
            for block in content_blocks:
                if block.get("type") in ("image", "gallery"):
                    images = block.get("images", [block])
                    for img in images:
                        if img.get("src") or img.get("url"):
                            if not img.get("alt"):
                                issues.append({
                                    "page": str(page.id),
                                    "slug": page.slug,
                                    "type": "missing_alt_text",
                                    "severity": "medium",
                                    "message": f"Image missing alt text on '{page.title}'",
                                })

        # Create audit record
        score = max(0, 100 - (len(issues) * 5))
        audit = SEOAudit.objects.create(
            site=site,
            org=site.org,
            overall_score=score,
            issues=issues,
            pages_analyzed=pages.count(),
            issues_found=len(issues),
            status="completed",
        )

        logger.info(f"SEO audit for site '{site.domain}': score={score}, issues={len(issues)}")
        return {
            "audit_id": str(audit.id),
            "score": score,
            "issues": len(issues),
            "pages": pages.count(),
        }

    except Site.DoesNotExist:
        return {"error": "site_not_found"}
    except Exception as e:
        logger.error(f"SEO audit failed: {e}")
        return {"error": str(e)}


@shared_task
def track_keyword_rankings(org_id):
    """Check search rankings for tracked keywords."""
    from .models import TrackedKeyword

    keywords = TrackedKeyword.objects.filter(org_id=org_id, is_active=True)

    # TODO: Integrate with Google Search Console API or a SERP API
    # For now, stub that logs the check
    for kw in keywords:
        # Store previous position for rank_change calculation
        if kw.current_position:
            kw.previous_position = kw.current_position
            kw.save(update_fields=["previous_position"])

    logger.info(f"Keyword ranking check stub for org {org_id}: {keywords.count()} keywords")
    return {"org_id": str(org_id), "keywords_checked": keywords.count()}


@shared_task
def generate_sitemap(site_id):
    """Generate XML sitemap for a site."""
    from apps.sites.models import Site, Page
    from django.utils import timezone

    try:
        site = Site.objects.get(id=site_id)
        pages = Page.objects.filter(site=site, is_published=True)

        domain = site.custom_domain or site.domain
        urls = []

        for page in pages:
            url = f"https://{domain}/{page.slug}" if page.slug != "home" else f"https://{domain}/"
            urls.append({
                "loc": url,
                "lastmod": page.updated_at.strftime("%Y-%m-%d"),
                "priority": "1.0" if page.slug == "home" else "0.8",
            })

        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for u in urls:
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{u['loc']}</loc>")
            xml_lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
            xml_lines.append(f"    <priority>{u['priority']}</priority>")
            xml_lines.append("  </url>")
        xml_lines.append("</urlset>")

        sitemap_xml = "\n".join(xml_lines)

        # Store in SEOSettings
        from .models import SEOSettings
        settings, _ = SEOSettings.objects.get_or_create(
            site=site, org=site.org,
        )
        settings.custom_sitemap = sitemap_xml
        settings.save(update_fields=["custom_sitemap"])

        logger.info(f"Generated sitemap for {domain}: {len(urls)} URLs")
        return {"site_id": str(site_id), "urls": len(urls)}

    except Site.DoesNotExist:
        return {"error": "site_not_found"}


@shared_task
def measure_page_speed(site_id):
    """Measure page speed metrics for a site."""
    from apps.sites.models import Site, Page
    from .models import PageSpeedMetrics

    try:
        site = Site.objects.get(id=site_id)
        pages = Page.objects.filter(site=site, is_published=True)[:10]

        # TODO: Integrate with Google PageSpeed Insights API
        # GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
        # ?url={page_url}&key={API_KEY}

        for page in pages:
            # Stub: create placeholder metrics
            PageSpeedMetrics.objects.update_or_create(
                page=page,
                org=site.org,
                defaults={
                    "performance_score": 0,
                    "fcp": 0,
                    "lcp": 0,
                    "cls": 0,
                    "tbt": 0,
                    "speed_index": 0,
                },
            )

        logger.info(f"Page speed metrics stub for site {site_id}")
        return {"site_id": str(site_id), "pages_measured": pages.count()}

    except Site.DoesNotExist:
        return {"error": "site_not_found"}


@shared_task
def check_internal_links(site_id):
    """Analyze internal linking opportunities."""
    from apps.sites.models import Site, Page
    from .models import InternalLinkSuggestion

    try:
        site = Site.objects.get(id=site_id)
        pages = list(Page.objects.filter(site=site, is_published=True))

        suggestions_created = 0
        for source in pages:
            source_text = ""
            for block in (source.content_blocks or []):
                source_text += " " + str(block.get("content", ""))
                source_text += " " + str(block.get("heading", ""))

            for target in pages:
                if source.id == target.id:
                    continue
                # Simple keyword matching — check if target title words appear in source
                title_words = target.title.lower().split()
                if len(title_words) >= 2:
                    phrase = " ".join(title_words[:3])
                    if phrase in source_text.lower():
                        _, created = InternalLinkSuggestion.objects.get_or_create(
                            org=site.org,
                            source_page=source,
                            target_page=target,
                            defaults={
                                "anchor_text": target.title,
                                "relevance_score": 0.7,
                            },
                        )
                        if created:
                            suggestions_created += 1

        logger.info(f"Internal link analysis for site {site_id}: {suggestions_created} suggestions")
        return {"site_id": str(site_id), "suggestions": suggestions_created}

    except Site.DoesNotExist:
        return {"error": "site_not_found"}
