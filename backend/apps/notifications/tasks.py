"""Celery tasks for notifications."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_email(notification_id):
    """Send a notification via email (SES)."""
    from .models import Notification

    try:
        notif = Notification.objects.select_related("org").get(id=notification_id)

        # Check user preferences
        from .models import NotificationPreference
        pref, _ = NotificationPreference.objects.get_or_create(
            user=notif.user,
            defaults={"email_enabled": True},
        )
        if not pref.email_enabled:
            logger.info(f"Email notifications disabled for user {notif.user_id}")
            return {"status": "skipped", "reason": "email_disabled"}

        send_mail(
            subject=notif.title,
            message=notif.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notif.user.email],
            fail_silently=True,
        )

        logger.info(f"Email notification sent: {notif.title}")
        return {"status": "sent", "notification_id": str(notification_id)}

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {"error": "not_found"}


@shared_task
def send_push_notification(notification_id):
    """Send push notification via WebSocket."""
    from .models import Notification
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    try:
        notif = Notification.objects.get(id=notification_id)
        channel_layer = get_channel_layer()

        # Send to user's personal channel group
        async_to_sync(channel_layer.group_send)(
            f"user_{notif.user_id}",
            {
                "type": "notification.message",
                "data": {
                    "id": str(notif.id),
                    "title": notif.title,
                    "message": notif.message,
                    "type": notif.notification_type,
                    "created_at": notif.created_at.isoformat(),
                },
            },
        )
        return {"status": "pushed"}

    except Notification.DoesNotExist:
        return {"error": "not_found"}
    except Exception as e:
        logger.error(f"Push notification failed: {e}")
        return {"error": str(e)}


@shared_task
def cleanup_old_notifications(days=30):
    """Delete read notifications older than N days."""
    from django.utils import timezone
    from datetime import timedelta
    from .models import Notification

    cutoff = timezone.now() - timedelta(days=days)
    deleted = Notification.objects.filter(
        is_read=True, created_at__lt=cutoff
    ).delete()
    logger.info(f"Cleaned up {deleted[0]} old notifications")
    return {"deleted": deleted[0]}
