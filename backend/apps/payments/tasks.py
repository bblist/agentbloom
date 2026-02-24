"""Celery tasks for Payments processing."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_stripe_webhook(self, payload, sig_header, site_id=None):
    """Process incoming Stripe webhook events."""
    import json
    from decimal import Decimal

    try:
        event = json.loads(payload) if isinstance(payload, str) else payload
        event_type = event.get("type", "")
        data = event.get("data", {}).get("object", {})

        logger.info(f"Processing Stripe event: {event_type}")

        if event_type == "checkout.session.completed":
            handle_checkout_completed(data, site_id)
        elif event_type == "invoice.paid":
            handle_invoice_paid(data, site_id)
        elif event_type == "invoice.payment_failed":
            handle_invoice_failed(data, site_id)
        elif event_type == "customer.subscription.updated":
            handle_subscription_updated(data, site_id)
        elif event_type == "customer.subscription.deleted":
            handle_subscription_deleted(data, site_id)
        elif event_type == "charge.refunded":
            handle_charge_refunded(data, site_id)
        elif event_type == "charge.dispute.created":
            handle_dispute_created(data, site_id)
        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")

        return {"event": event_type, "status": "processed"}

    except Exception as exc:
        logger.error(f"Stripe webhook processing failed: {exc}")
        self.retry(exc=exc, countdown=30)


def handle_checkout_completed(data, site_id):
    """Handle successful checkout."""
    from .models import Payment

    stripe_session_id = data.get("id")
    payment_intent = data.get("payment_intent")
    amount = data.get("amount_total", 0)
    currency = data.get("currency", "usd")

    if site_id:
        from apps.sites.models import Site
        try:
            site = Site.objects.get(id=site_id)
            Payment.objects.filter(
                org=site.org,
                stripe_payment_intent_id=payment_intent,
            ).update(status="completed")
        except Exception as e:
            logger.warning(f"Could not update payment for checkout: {e}")


def handle_invoice_paid(data, site_id):
    """Handle paid invoice."""
    from .models import Invoice

    stripe_invoice_id = data.get("id")
    try:
        Invoice.objects.filter(
            stripe_invoice_id=stripe_invoice_id,
        ).update(status="paid")
        logger.info(f"Invoice {stripe_invoice_id} marked as paid")
    except Exception as e:
        logger.warning(f"Could not update invoice: {e}")


def handle_invoice_failed(data, site_id):
    """Handle failed invoice payment."""
    from .models import Invoice, Subscription

    stripe_invoice_id = data.get("id")
    subscription_id = data.get("subscription")

    try:
        Invoice.objects.filter(
            stripe_invoice_id=stripe_invoice_id,
        ).update(status="overdue")
    except Exception:
        pass

    # Mark subscription as past_due
    if subscription_id:
        Subscription.objects.filter(
            stripe_subscription_id=subscription_id,
        ).update(status="past_due")


def handle_subscription_updated(data, site_id):
    """Handle subscription status changes."""
    from .models import Subscription

    stripe_sub_id = data.get("id")
    status_map = {
        "active": "active",
        "past_due": "past_due",
        "canceled": "cancelled",
        "trialing": "trialing",
        "unpaid": "past_due",
    }
    stripe_status = data.get("status", "")
    our_status = status_map.get(stripe_status, stripe_status)

    Subscription.objects.filter(
        stripe_subscription_id=stripe_sub_id,
    ).update(status=our_status)


def handle_subscription_deleted(data, site_id):
    """Handle subscription cancellation."""
    from .models import Subscription

    stripe_sub_id = data.get("id")
    Subscription.objects.filter(
        stripe_subscription_id=stripe_sub_id,
    ).update(status="cancelled")


def handle_charge_refunded(data, site_id):
    """Handle refund completion."""
    from .models import Payment, Refund

    charge_id = data.get("id")
    refunded = data.get("refunded", False)

    if refunded:
        Payment.objects.filter(
            stripe_charge_id=charge_id,
        ).update(status="refunded")


def handle_dispute_created(data, site_id):
    """Handle charge dispute/chargeback."""
    from .models import Payment

    charge_id = data.get("charge")
    Payment.objects.filter(
        stripe_charge_id=charge_id,
    ).update(status="disputed")
    logger.warning(f"Dispute created for charge {charge_id}")


@shared_task
def sync_stripe_subscriptions(org_id):
    """Sync subscription statuses from Stripe."""
    from .models import StripeConnection, Subscription
    import os

    try:
        conn = StripeConnection.objects.get(org_id=org_id, status="active")
    except StripeConnection.DoesNotExist:
        return {"error": "no_stripe_connection"}

    # TODO: Use Stripe API to list and sync subscriptions
    # import stripe
    # stripe.api_key = conn.stripe_secret_key (decrypted)
    # subs = stripe.Subscription.list(limit=100)
    # for sub in subs.auto_paging_iter(): ...

    logger.info(f"Stripe subscription sync stub for org {org_id}")
    return {"org_id": str(org_id), "status": "stub"}


@shared_task
def generate_revenue_snapshot(org_id):
    """Generate a daily revenue snapshot for an org."""
    from django.utils import timezone
    from django.db.models import Sum, Count
    from datetime import timedelta
    from .models import Payment, RevenueSnapshot

    today = timezone.now().date()
    start = timezone.datetime.combine(today, timezone.datetime.min.time())
    end = start + timedelta(days=1)

    try:
        payments = Payment.objects.filter(
            org_id=org_id,
            status="completed",
            created_at__gte=start,
            created_at__lt=end,
        )

        agg = payments.aggregate(
            total=Sum("amount"),
            count=Count("id"),
        )

        refund_agg = Payment.objects.filter(
            org_id=org_id,
            status="refunded",
            created_at__gte=start,
            created_at__lt=end,
        ).aggregate(total=Sum("amount"))

        snapshot, _ = RevenueSnapshot.objects.update_or_create(
            org_id=org_id,
            date=today,
            defaults={
                "gross_revenue": agg["total"] or 0,
                "net_revenue": (agg["total"] or 0) - (refund_agg["total"] or 0),
                "refunds": refund_agg["total"] or 0,
                "transaction_count": agg["count"] or 0,
            },
        )

        return {
            "org_id": str(org_id),
            "date": str(today),
            "gross": str(snapshot.gross_revenue),
        }

    except Exception as e:
        logger.error(f"Revenue snapshot failed: {e}")
        return {"error": str(e)}


@shared_task
def send_payment_receipt(payment_id):
    """Send payment receipt email to customer."""
    from .models import Payment

    try:
        payment = Payment.objects.select_related("org").get(id=payment_id)
        send_mail(
            subject=f"Payment Receipt — {payment.org.name}",
            message=(
                f"Thank you for your payment.\n\n"
                f"Amount: ${payment.amount}\n"
                f"Date: {payment.created_at.strftime('%B %d, %Y')}\n"
                f"Reference: {payment.id}\n\n"
                f"Thank you for your business!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.customer_email],
            fail_silently=True,
        )
        logger.info(f"Receipt email sent for payment {payment_id}")
        return {"payment_id": str(payment_id), "status": "sent"}
    except Payment.DoesNotExist:
        return {"error": "not_found"}


@shared_task
def process_dunning(org_id):
    """Send dunning emails for failed subscription payments."""
    from django.utils import timezone
    from datetime import timedelta
    from .models import Subscription

    past_due = Subscription.objects.filter(
        org_id=org_id,
        status="past_due",
    )

    for sub in past_due:
        days_overdue = (timezone.now() - sub.updated_at).days
        # Dunning schedule: Day 1, 3, 7, 14
        if days_overdue in [1, 3, 7, 14]:
            send_mail(
                subject="Action Required: Payment Past Due",
                message=(
                    f"Your subscription payment is {days_overdue} day(s) overdue.\n"
                    f"Please update your payment method to avoid service interruption.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[sub.org.owner.email if hasattr(sub.org, 'owner') else settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            logger.info(f"Dunning email day {days_overdue} for sub {sub.id}")

    return {"org_id": str(org_id), "past_due_count": past_due.count()}
