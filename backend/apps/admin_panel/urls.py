from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"feature-flags", views.FeatureFlagViewSet, basename="feature-flag")
router.register(r"audit-log", views.AdminAuditLogViewSet, basename="audit-log")
router.register(r"tickets", views.SupportTicketViewSet, basename="support-ticket")
router.register(r"moderation", views.ContentModerationQueueViewSet, basename="moderation")
router.register(r"system-health", views.SystemHealthCheckViewSet, basename="health-check")
router.register(r"impersonation", views.ImpersonationSessionViewSet, basename="impersonation")
router.register(r"lifecycle", views.UserLifecycleEventViewSet, basename="lifecycle")
router.register(r"revenue", views.RevenueAnalyticsViewSet, basename="revenue-analytics")
router.register(r"metrics", views.PlatformMetricsViewSet, basename="platform-metrics")
router.register(r"users", views.AdminUserViewSet, basename="admin-user")

urlpatterns = [
    path("", include(router.urls)),
]
