"""Celery tasks for sites operations."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import os
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

        # Send email notification
        send_mail(
            subject=f"New form submission: {submission.form.name}",
            message=(
                f"You have a new form submission on {submission.form.site.name}.\n\n"
                f"Form: {submission.form.name}\n"
                f"Data: {submission.data}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[org.owner.email if hasattr(org, 'owner') else settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )

        # Create/update CRM contact if email provided
        submission_email = submission.data.get('email')
        if submission_email:
            try:
                from apps.email_crm.models import Contact
                Contact.objects.get_or_create(
                    org=org,
                    email=submission_email,
                    defaults={
                        "first_name": submission.data.get("first_name", ""),
                        "last_name": submission.data.get("last_name", ""),
                        "source": "form_submission",
                    },
                )
            except Exception as e:
                logger.warning(f"Could not create CRM contact: {e}")

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
            # Upload rendered HTML to S3
            import boto3
            s3 = boto3.client("s3", region_name=settings.AWS_REGION)
            bucket = settings.AWS_S3_BUCKET_SITES
            key = f"sites/{site.id}/{page.slug}.html"
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=html.encode("utf-8"),
                ContentType="text/html",
                CacheControl="public, max-age=3600",
            )
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
    import boto3

    distribution_id = settings.AWS_CLOUDFRONT_DISTRIBUTION_ID if hasattr(settings, 'AWS_CLOUDFRONT_DISTRIBUTION_ID') else os.getenv("AWS_CLOUDFRONT_DISTRIBUTION_ID", "")
    if not distribution_id:
        logger.warning(f"No CloudFront distribution ID configured, skipping invalidation for site {site_id}")
        return {"status": "skipped", "reason": "no_distribution_id"}

    cf = boto3.client("cloudfront", region_name=settings.AWS_REGION)
    cf.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            "Paths": {
                "Quantity": 1,
                "Items": [f"/sites/{site_id}/*"],
            },
            "CallerReference": f"site-{site_id}-{__import__('time').time()}",
        },
    )
    logger.info(f"CDN invalidation created for site {site_id}")
    return {"status": "invalidated"}
