"""Celery tasks for bookings."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_booking_confirmation(booking_id):
    """Send booking confirmation email."""
    from .models import Booking

    try:
        booking = Booking.objects.select_related("service", "org").get(id=booking_id)
        # TODO: Send confirmation email via SES
        logger.info(f"Confirmation sent for booking {booking.customer_name} - {booking.service.name}")
        return {"status": "sent", "booking_id": str(booking_id)}
    except Booking.DoesNotExist:
        return {"error": "not_found"}


@shared_task
def send_booking_reminders():
    """Send reminders for bookings happening in the next 24 hours."""
    from django.utils import timezone
    from datetime import timedelta
    from .models import Booking

    now = timezone.now()
    window = now + timedelta(hours=24)

    bookings = Booking.objects.filter(
        start_time__gte=now,
        start_time__lte=window,
        status="confirmed",
        reminder_sent=False,
    ).select_related("service")

    sent = 0
    for booking in bookings:
        # TODO: Send reminder email via SES
        booking.reminder_sent = True
        booking.save(update_fields=["reminder_sent"])
        sent += 1

    logger.info(f"Sent {sent} booking reminders")
    return {"sent": sent}


@shared_task
def sync_google_calendar(connection_id):
    """Sync bookings with Google Calendar."""
    from .models import GoogleCalendarConnection
    # TODO: Implement Google Calendar API sync
    logger.info(f"Google Calendar sync for connection {connection_id} — not yet implemented")
    return {"status": "pending_implementation"}


@shared_task
def aggregate_booking_analytics(org_id):
    """Aggregate booking analytics for the current month."""
    from django.utils import timezone
    from .models import Booking, BookingAnalytics, Service

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    services = Service.objects.filter(org_id=org_id)

    for service in services:
        bookings = Booking.objects.filter(
            service=service,
            start_time__gte=month_start,
            start_time__lt=now,
        )

        analytics, _ = BookingAnalytics.objects.update_or_create(
            org_id=org_id,
            service=service,
            period=month_start.date(),
            defaults={
                "total_bookings": bookings.count(),
                "completed": bookings.filter(status="completed").count(),
                "cancelled": bookings.filter(status="cancelled").count(),
                "no_shows": bookings.filter(status="no_show").count(),
                "revenue": sum(b.payment_amount for b in bookings.filter(payment_status="paid")),
            },
        )

    logger.info(f"Booking analytics aggregated for org {org_id}")
    return {"services_processed": services.count()}
