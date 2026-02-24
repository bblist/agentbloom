"""Celery tasks for Admin Panel operations."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def aggregate_platform_metrics():
    """Aggregate daily platform-wide metrics."""
    from django.utils import timezone
    from django.db.models import Count, Sum, Avg
    from .models import PlatformMetrics

    today = timezone.now().date()

    try:
        from apps.users.models import Organization, User

        total_orgs = Organization.objects.count()
        active_orgs = Organization.objects.filter(is_active=True).count()
        total_users = User.objects.count()

        # Sites metrics
        from apps.sites.models import Site
        total_sites = Site.objects.count()
        published_sites = Site.objects.filter(is_published=True).count()

        # Agent metrics
        from apps.agent.models import Conversation
        from datetime import timedelta
        yesterday = today - timedelta(days=1)
        daily_conversations = Conversation.objects.filter(
            created_at__date=today,
        ).count()

        # Support metrics
        from .models import SupportTicket
        open_tickets = SupportTicket.objects.filter(
            status__in=["open", "in_progress"],
        ).count()

        metrics, _ = PlatformMetrics.objects.update_or_create(
            date=today,
            defaults={
                "total_organizations": total_orgs,
                "active_organizations": active_orgs,
                "total_users": total_users,
                "total_sites": total_sites,
                "published_sites": published_sites,
                "daily_conversations": daily_conversations,
                "open_support_tickets": open_tickets,
            },
        )

        logger.info(f"Platform metrics aggregated for {today}")
        return {
            "date": str(today),
            "orgs": total_orgs,
            "users": total_users,
            "sites": total_sites,
        }

    except Exception as e:
        logger.error(f"Platform metrics aggregation failed: {e}")
        return {"error": str(e)}


@shared_task
def aggregate_revenue_analytics():
    """Aggregate revenue analytics across all orgs."""
    from django.utils import timezone
    from django.db.models import Sum, Count
    from datetime import timedelta

    today = timezone.now().date()
    month_start = today.replace(day=1)

    try:
        from apps.payments.models import Payment, Subscription
        from .models import RevenueAnalytics

        # Monthly revenue
        monthly_payments = Payment.objects.filter(
            status="completed",
            created_at__date__gte=month_start,
            created_at__date__lte=today,
        )
        monthly_agg = monthly_payments.aggregate(
            total=Sum("amount"),
            count=Count("id"),
        )

        # MRR from active subscriptions
        active_subs = Subscription.objects.filter(status="active")
        mrr = active_subs.aggregate(total=Sum("amount"))["total"] or 0

        # Churn: cancelled this month
        churned = Subscription.objects.filter(
            status="cancelled",
            updated_at__date__gte=month_start,
        ).count()

        total_subs = active_subs.count() + churned
        churn_rate = (churned / total_subs * 100) if total_subs > 0 else 0

        analytics, _ = RevenueAnalytics.objects.update_or_create(
            date=today,
            defaults={
                "mrr": mrr,
                "arr": mrr * 12,
                "total_revenue": monthly_agg["total"] or 0,
                "transaction_count": monthly_agg["count"] or 0,
                "churn_rate": round(churn_rate, 2),
                "active_subscriptions": active_subs.count(),
            },
        )

        logger.info(f"Revenue analytics aggregated for {today}: MRR=${mrr}")
        return {
            "date": str(today),
            "mrr": str(mrr),
            "transactions": monthly_agg["count"] or 0,
        }

    except Exception as e:
        logger.error(f"Revenue analytics failed: {e}")
        return {"error": str(e)}


@shared_task
def cleanup_audit_logs(days=90):
    """Delete old audit log entries."""
    from django.utils import timezone
    from datetime import timedelta
    from .models import AdminAuditLog

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = AdminAuditLog.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Cleaned up {deleted} audit logs older than {days} days")
    return {"deleted": deleted}


@shared_task
def run_system_health_check():
    """Run automated system health checks."""
    from django.utils import timezone
    from .models import SystemHealthCheck
    import time

    checks = {}

    # Database check
    try:
        from django.db import connection
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_latency = round((time.time() - start) * 1000, 2)
        checks["database"] = {"status": "healthy", "latency_ms": db_latency}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}

    # Redis check
    try:
        from django.core.cache import cache
        start = time.time()
        cache.set("health_check", "ok", 10)
        val = cache.get("health_check")
        redis_latency = round((time.time() - start) * 1000, 2)
        checks["redis"] = {
            "status": "healthy" if val == "ok" else "degraded",
            "latency_ms": redis_latency,
        }
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}

    # Celery check (we're running in Celery, so it's working)
    checks["celery"] = {"status": "healthy"}

    # Disk usage
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        disk_pct = round(used / total * 100, 1)
        checks["disk"] = {
            "status": "healthy" if disk_pct < 85 else "degraded" if disk_pct < 95 else "unhealthy",
            "used_percent": disk_pct,
            "free_gb": round(free / (1024**3), 1),
        }
    except Exception:
        checks["disk"] = {"status": "unknown"}

    # Memory usage
    try:
        import os
        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            mem_total = int(lines[0].split()[1])
            mem_available = int(lines[2].split()[1])
            mem_pct = round((1 - mem_available / mem_total) * 100, 1)
            checks["memory"] = {
                "status": "healthy" if mem_pct < 85 else "degraded",
                "used_percent": mem_pct,
            }
        else:
            checks["memory"] = {"status": "unknown", "note": "non-linux"}
    except Exception:
        checks["memory"] = {"status": "unknown"}

    # Overall status
    statuses = [c.get("status") for c in checks.values()]
    if "unhealthy" in statuses:
        overall = "unhealthy"
    elif "degraded" in statuses:
        overall = "degraded"
    else:
        overall = "healthy"

    health = SystemHealthCheck.objects.create(
        status=overall,
        checks=checks,
        response_time_ms=sum(
            c.get("latency_ms", 0) for c in checks.values()
        ),
    )

    logger.info(f"System health check: {overall}")
    return {"status": overall, "checks": checks}


@shared_task
def expire_impersonation_sessions():
    """End expired impersonation sessions."""
    from django.utils import timezone
    from .models import ImpersonationSession

    expired = ImpersonationSession.objects.filter(
        ended_at__isnull=True,
        expires_at__lte=timezone.now(),
    )
    count = expired.count()
    expired.update(ended_at=timezone.now())
    if count:
        logger.info(f"Expired {count} impersonation sessions")
    return {"expired": count}


@shared_task
def check_content_moderation_queue():
    """Alert staff if moderation queue is growing."""
    from .models import ContentModerationQueue

    pending = ContentModerationQueue.objects.filter(status="pending").count()
    if pending > 50:
        logger.warning(f"Content moderation queue has {pending} pending items")
        from apps.notifications.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        for admin in User.objects.filter(is_staff=True):
            Notification.objects.create(
                user=admin,
                title="Moderation Queue Alert",
                message=f"There are {pending} items pending moderation.",
                notification_type="system",
                channel="in_app",
            )

    return {"pending": pending}
