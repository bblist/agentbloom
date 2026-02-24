"""Celery tasks for sites operations."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_site_preview(site_id):
    """Generate a preview screenshot of the site homepage."""
    # TODO: Use Playwright or similar to capture screenshot
    logger.info(f"Preview generation for site {site_id} — not yet implemented")
    return {"status": "pending_implementation"}


@shared_task
def process_form_submission(submission_id):
    """Process a form submission — send notification email, create CRM contact."""
    from .models import FormSubmission
    from apps.notifications.models import Notification

    try:
        submission = FormSubmission.objects.select_related("form__site__org").get(id=submission_id)
        org = submission.form.site.org

        # Create notification
        Notification.objects.create(
            org=org,
            title=f"New form submission: {submission.form.name}",
            message=f"From: {submission.data.get('email', 'Unknown')}",
            notification_type="form_submission",
            data={"submission_id": str(submission_id)},
        )

        # TODO: Send email notification via SES
        # TODO: Create/update CRM contact

        return {"status": "processed", "submission_id": str(submission_id)}

    except FormSubmission.DoesNotExist:
        logger.error(f"FormSubmission {submission_id} not found")
        return {"error": "not_found"}


@shared_task
def publish_site_to_cdn(site_id):
    """Render all published pages and deploy to CDN / S3."""
    from .models import Site
    from .renderer import render_page_html

    try:
        site = Site.objects.prefetch_related("pages").get(id=site_id)
        pages = site.pages.filter(status="published")
        rendered = []

        for page in pages:
            html = render_page_html(page.content_blocks, site.global_styles, {
                "title": page.seo_title or page.title,
                "description": page.seo_description or "",
            })
            # TODO: Upload to S3 with CloudFront
            rendered.append(page.slug)

        site.status = "published"
        site.save(update_fields=["status"])

        logger.info(f"Published site {site.name}: {len(rendered)} pages")
        return {"status": "published", "pages": rendered}

    except Site.DoesNotExist:
        logger.error(f"Site {site_id} not found")
        return {"error": "not_found"}


@shared_task
def invalidate_cdn_cache(site_id):
    """Invalidate CloudFront cache for a site."""
    # TODO: Call CloudFront invalidation API
    logger.info(f"CDN invalidation for site {site_id} — not yet implemented")
    return {"status": "pending_implementation"}
