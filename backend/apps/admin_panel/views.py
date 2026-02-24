from rest_framework import viewsets, status, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone

from .models import (
    FeatureFlag, FeatureFlagHistory, AdminAuditLog, SupportTicket,
    SupportMessage, ContentModerationQueue, SystemHealthCheck,
    ImpersonationSession, UserLifecycleEvent, RevenueAnalytics,
    PlatformMetrics,
)
from .serializers import (
    FeatureFlagSerializer, FeatureFlagHistorySerializer,
    AdminAuditLogSerializer, SupportTicketListSerializer,
    SupportTicketDetailSerializer, SupportMessageSerializer,
    ContentModerationQueueSerializer, SystemHealthCheckSerializer,
    ImpersonationSessionSerializer, UserLifecycleEventSerializer,
    RevenueAnalyticsSerializer, PlatformMetricsSerializer,
)

User = get_user_model()


class FeatureFlagViewSet(viewsets.ModelViewSet):
    serializer_class = FeatureFlagSerializer
    permission_classes = [IsAdminUser]
    queryset = FeatureFlag.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        old = self.get_object()
        old_data = FeatureFlagSerializer(old).data

        instance = serializer.save()

        FeatureFlagHistory.objects.create(
            flag=instance,
            changed_by=self.request.user,
            old_value=old_data,
            new_value=FeatureFlagSerializer(instance).data,
        )

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        flag = self.get_object()
        old_enabled = flag.is_enabled
        flag.is_enabled = not flag.is_enabled
        flag.save(update_fields=["is_enabled", "updated_at"])
        FeatureFlagHistory.objects.create(
            flag=flag,
            changed_by=request.user,
            old_value={"is_enabled": old_enabled},
            new_value={"is_enabled": flag.is_enabled},
        )
        return Response({"is_enabled": flag.is_enabled})

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        flag = self.get_object()
        entries = flag.history.all()[:50]
        return Response(FeatureFlagHistorySerializer(entries, many=True).data)


class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsAdminUser]
    queryset = AdminAuditLog.objects.select_related("admin_user").all()


class SupportTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = SupportTicket.objects.select_related("user", "org").annotate(
            message_count=Count("messages"),
        )
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return SupportTicketListSerializer
        return SupportTicketDetailSerializer

    def perform_create(self, serializer):
        serializer.save(org=self.request.org, user=self.request.user)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        ticket = self.get_object()
        content = request.data.get("content")
        if not content:
            return Response({"error": "content required"}, status=400)
        msg = SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            content=content,
            is_internal=request.data.get("is_internal", False),
        )
        ticket.status = "in_progress"
        ticket.save(update_fields=["status", "updated_at"])
        return Response(SupportMessageSerializer(msg).data, status=201)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = "resolved"
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response({"status": "resolved"})

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        assignee_id = request.data.get("user_id")
        if not assignee_id:
            return Response({"error": "user_id required"}, status=400)
        ticket.assigned_to_id = assignee_id
        ticket.save(update_fields=["assigned_to", "updated_at"])
        return Response({"assigned_to": str(assignee_id)})


class ContentModerationQueueViewSet(viewsets.ModelViewSet):
    serializer_class = ContentModerationQueueSerializer
    permission_classes = [IsAdminUser]
    queryset = ContentModerationQueue.objects.all()

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        item = self.get_object()
        item.status = "approved"
        item.reviewed_by = request.user
        item.reviewed_at = timezone.now()
        item.save(update_fields=["status", "reviewed_by", "reviewed_at"])
        return Response({"status": "approved"})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        item = self.get_object()
        item.status = "rejected"
        item.reviewed_by = request.user
        item.reviewed_at = timezone.now()
        item.save(update_fields=["status", "reviewed_by", "reviewed_at"])
        return Response({"status": "rejected"})


class SystemHealthCheckViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SystemHealthCheckSerializer
    permission_classes = [IsAdminUser]
    queryset = SystemHealthCheck.objects.all()

    @action(detail=False, methods=["post"])
    def run_check(self, request):
        """Run health checks on all services."""
        import time
        services = ["database", "redis", "llm", "stripe", "ses"]
        results = []
        for svc in services:
            start = time.time()
            svc_status = "healthy"
            details = {}

            if svc == "database":
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                except Exception as e:
                    svc_status = "down"
                    details["error"] = str(e)
            elif svc == "redis":
                try:
                    from django.core.cache import cache
                    cache.set("health_check", "ok", 5)
                    val = cache.get("health_check")
                    if val != "ok":
                        svc_status = "degraded"
                except Exception as e:
                    svc_status = "down"
                    details["error"] = str(e)
            # Other services would be checked similarly

            elapsed = int((time.time() - start) * 1000)
            check = SystemHealthCheck.objects.create(
                service=svc,
                status=svc_status,
                response_time_ms=elapsed,
                details=details,
            )
            results.append(SystemHealthCheckSerializer(check).data)

        return Response({"checks": results})

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Get latest health status for each service."""
        services = ["database", "redis", "llm", "stripe", "ses"]
        latest = {}
        for svc in services:
            check = SystemHealthCheck.objects.filter(service=svc).first()
            if check:
                latest[svc] = SystemHealthCheckSerializer(check).data
            else:
                latest[svc] = {"status": "unknown"}
        return Response(latest)


class ImpersonationSessionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ImpersonationSessionSerializer
    permission_classes = [IsAdminUser]
    queryset = ImpersonationSession.objects.select_related("admin_user", "target_user").all()


class UserLifecycleEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserLifecycleEventSerializer
    permission_classes = [IsAdminUser]
    queryset = UserLifecycleEvent.objects.select_related("user").all()


class RevenueAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RevenueAnalyticsSerializer
    permission_classes = [IsAdminUser]
    queryset = RevenueAnalytics.objects.all()

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Get the most recent revenue analytics snapshot."""
        entry = RevenueAnalytics.objects.first()
        if not entry:
            return Response({"error": "No analytics data yet"}, status=404)
        return Response(RevenueAnalyticsSerializer(entry).data)


class PlatformMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlatformMetricsSerializer
    permission_classes = [IsAdminUser]
    queryset = PlatformMetrics.objects.all()

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Get today's platform metrics."""
        from datetime import date
        try:
            metrics = PlatformMetrics.objects.get(date=date.today())
            return Response(PlatformMetricsSerializer(metrics).data)
        except PlatformMetrics.DoesNotExist:
            return Response({"error": "No metrics for today"}, status=404)


class AdminUserSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "full_name",
            "is_active", "is_staff", "is_superuser",
            "created_at", "last_login",
        ]
        read_only_fields = fields


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin-only view to list / retrieve platform users."""
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("-created_at")
    filterset_fields = ["is_active", "is_staff"]
    search_fields = ["email", "full_name"]

    @action(detail=True, methods=["post"])
    def impersonate(self, request, pk=None):
        """Start an impersonation session for the target user."""
        target = self.get_object()
        if target.is_superuser:
            return Response(
                {"error": "Cannot impersonate a superuser"},
                status=status.HTTP_403_FORBIDDEN,
            )
        session = ImpersonationSession.objects.create(
            admin_user=request.user,
            target_user=target,
            reason=request.data.get("reason", ""),
        )
        return Response(
            ImpersonationSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )
