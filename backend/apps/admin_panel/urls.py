from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"feature-flags", views.FeatureFlagViewSet, basename="feature-flag")
router.register(r"audit-logs", views.AdminAuditLogViewSet, basename="audit-log")
router.register(r"support-tickets", views.SupportTicketViewSet, basename="support-ticket")
router.register(r"moderation", views.ContentModerationQueueViewSet, basename="moderation")
router.register(r"health", views.SystemHealthCheckViewSet, basename="health-check")
router.register(r"impersonation", views.ImpersonationSessionViewSet, basename="impersonation")
router.register(r"lifecycle", views.UserLifecycleEventViewSet, basename="lifecycle")
router.register(r"revenue-analytics", views.RevenueAnalyticsViewSet, basename="revenue-analytics")
router.register(r"metrics", views.PlatformMetricsViewSet, basename="platform-metrics")

urlpatterns = [
    path("", include(router.urls)),
]
