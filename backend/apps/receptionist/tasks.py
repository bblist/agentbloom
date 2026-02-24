"""
Celery tasks for the Receptionist app.

- Aggregate daily chat analytics
- Clean up stale sessions
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.db.models import Avg, Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def aggregate_daily_analytics():
    """Run at end of day to aggregate chat analytics per org."""
    from apps.organizations.models import Organization
    from .models import ChatSession, ChatMessage, ChatAnalytics

    yesterday = (timezone.now() - timedelta(days=1)).date()

    for org in Organization.objects.all():
        sessions = ChatSession.objects.filter(
            org=org,
            created_at__date=yesterday,
        )
        total = sessions.count()
        if total == 0:
            continue

        ai_resolved = sessions.filter(status="closed").count()
        transferred = sessions.filter(status="transferred").count()

        # Count leads (sessions where visitor_email is set)
        leads = sessions.exclude(visitor_email="").count()

        # Average messages per session
        avg_msgs = (
            ChatMessage.objects.filter(session__in=sessions)
            .values("session")
            .annotate(cnt=Count("id"))
            .aggregate(avg=Avg("cnt"))["avg"]
            or 0
        )

        # Average sentiment
        avg_sentiment = sessions.aggregate(avg=Avg("sentiment_score"))["avg"]

        ChatAnalytics.objects.update_or_create(
            org=org,
            date=yesterday,
            defaults={
                "total_sessions": total,
                "ai_resolved": ai_resolved,
                "transferred": transferred,
                "leads_collected": leads,
                "appointments_booked": 0,
                "avg_messages_per_session": round(avg_msgs, 1),
                "avg_sentiment": avg_sentiment,
            },
        )
        logger.info(f"Analytics aggregated for {org.name} on {yesterday}")


@shared_task
def close_stale_sessions():
    """Close sessions that have been inactive for more than 30 minutes."""
    from .models import ChatSession

    threshold = timezone.now() - timedelta(minutes=30)
    stale = ChatSession.objects.filter(
        status="active",
        updated_at__lt=threshold,
    )
    count = stale.update(status="closed", closed_at=timezone.now())
    if count:
        logger.info(f"Closed {count} stale chat sessions")
