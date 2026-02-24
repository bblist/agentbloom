"""Celery tasks for email/CRM operations."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_campaign_emails(self, campaign_id):
    """Send campaign emails to all contacts in the segment."""
    from .models import Campaign, CampaignEvent, Contact

    try:
        campaign = Campaign.objects.select_related("segment", "template").get(id=campaign_id)
        contacts = campaign.segment.get_contacts() if campaign.segment else Contact.objects.filter(
            org=campaign.org, is_subscribed=True
        )

        sent_count = 0
        for contact in contacts:
            try:
                send_mail(
                    subject=campaign.subject or campaign.name,
                    message=campaign.template.body if hasattr(campaign.template, 'body') else str(campaign.template),
                    from_email=f"{campaign.org.name} <{settings.DEFAULT_FROM_EMAIL}>",
                    recipient_list=[contact.email],
                    html_message=getattr(campaign.template, 'html_body', None),
                    fail_silently=False,
                )

                CampaignEvent.objects.create(
                    campaign=campaign,
                    contact=contact,
                    event_type="sent",
                )
                sent_count += 1
            except Exception as e:
                CampaignEvent.objects.create(
                    campaign=campaign,
                    contact=contact,
                    event_type="failed",
                    metadata={"error": str(e)},
                )
                logger.error(f"Failed to send to {contact.email}: {e}")

        campaign.status = "sent"
        campaign.sent_count = sent_count
        campaign.save(update_fields=["status", "sent_count"])

        logger.info(f"Campaign {campaign.name}: sent {sent_count} emails")
        return {"campaign_id": str(campaign_id), "sent": sent_count}

    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
        return {"error": "not_found"}
    except Exception as exc:
        logger.error(f"Campaign send failed: {exc}")
        self.retry(exc=exc, countdown=30)


@shared_task
def process_email_event(event_data):
    """Process SES/SNS webhook events (bounce, complaint, open, click)."""
    from .models import CampaignEvent, Contact

    event_type = event_data.get("eventType", "")
    email = event_data.get("mail", {}).get("destination", [None])[0]

    if not email:
        return {"error": "no_email"}

    if event_type == "Bounce":
        # Mark contact as bounced
        Contact.objects.filter(email=email).update(is_subscribed=False)
        logger.info(f"Bounce: unsubscribed {email}")
    elif event_type == "Complaint":
        Contact.objects.filter(email=email).update(is_subscribed=False)
        logger.info(f"Complaint: unsubscribed {email}")

    return {"event_type": event_type, "email": email}


@shared_task
def update_contact_scores(org_id):
    """Recalculate lead scores for all contacts in an org."""
    from .models import Contact, ScoringRule

    rules = ScoringRule.objects.filter(org_id=org_id, is_active=True)
    contacts = Contact.objects.filter(org_id=org_id)

    updated = 0
    for contact in contacts:
        score = 0
        for rule in rules:
            # Simple rule matching
            field_val = contact.custom_fields.get(rule.field, "")
            if rule.operator == "equals" and str(field_val) == str(rule.value):
                score += rule.points
            elif rule.operator == "contains" and str(rule.value) in str(field_val):
                score += rule.points
            elif rule.operator == "exists" and field_val:
                score += rule.points
        contact.lead_score = score
        contact.save(update_fields=["lead_score"])
        updated += 1

    logger.info(f"Updated scores for {updated} contacts in org {org_id}")
    return {"updated": updated}


@shared_task
def import_contacts_csv(org_id, csv_data, list_name="Imported"):
    """Import contacts from CSV data."""
    from .models import Contact
    import csv
    import io

    reader = csv.DictReader(io.StringIO(csv_data))
    created, skipped = 0, 0

    for row in reader:
        email = row.get("email", "").strip()
        if not email:
            skipped += 1
            continue

        _, was_created = Contact.objects.get_or_create(
            org_id=org_id,
            email=email,
            defaults={
                "first_name": row.get("first_name", ""),
                "last_name": row.get("last_name", ""),
                "phone": row.get("phone", ""),
                "source": "import",
                "tags": [list_name],
            },
        )
        if was_created:
            created += 1
        else:
            skipped += 1

    logger.info(f"CSV import: {created} created, {skipped} skipped")
    return {"created": created, "skipped": skipped}
