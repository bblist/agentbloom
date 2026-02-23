"""
AgentBloom URL Configuration
"""

from django.contrib import admin
from django.urls import include, path

from apps.users.views import HealthCheckView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Health check
    path("api/health/", HealthCheckView.as_view(), name="health-check"),
    # API v1
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/sites/", include("apps.sites.urls")),
    path("api/v1/agent/", include("apps.agent.urls")),
    path("api/v1/email/", include("apps.email_crm.urls")),
    path("api/v1/courses/", include("apps.courses.urls")),
    path("api/v1/calendar/", include("apps.calendar_booking.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
    path("api/v1/kb/", include("apps.kb.urls")),
    path("api/v1/seo/", include("apps.seo.urls")),
    path("api/v1/admin-panel/", include("apps.admin_panel.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/webhooks/", include("apps.webhooks.urls")),
    # Allauth
    path("accounts/", include("allauth.urls")),
]
