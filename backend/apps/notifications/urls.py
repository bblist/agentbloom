from django.urls import path
from . import views


# Manual URL patterns to avoid double-nesting (notifications/notifications/)
# Frontend expects: /api/v1/notifications/, /api/v1/notifications/<id>/read/, etc.
urlpatterns = [
    # Notifications
    path(
        "",
        views.NotificationViewSet.as_view({"get": "list"}),
        name="notification-list",
    ),
    path(
        "<str:pk>/",
        views.NotificationViewSet.as_view(
            {"get": "retrieve", "delete": "destroy"}
        ),
        name="notification-detail",
    ),
    path(
        "<str:pk>/read/",
        views.NotificationViewSet.as_view({"post": "mark_read"}),
        name="notification-mark-read",
    ),
    path(
        "read-all/",
        views.NotificationViewSet.as_view({"post": "mark_all_read"}),
        name="notification-mark-all-read",
    ),
    path(
        "unread-count/",
        views.NotificationViewSet.as_view({"get": "unread_count"}),
        name="notification-unread-count",
    ),
    # Notification Preferences (singleton for current user)
    path(
        "preferences/",
        views.NotificationPreferenceSingletonView.as_view(),
        name="notification-preferences",
    ),
    # Activity Feed
    path(
        "activity-feed/",
        views.ActivityFeedViewSet.as_view({"get": "list"}),
        name="activity-feed",
    ),
]
