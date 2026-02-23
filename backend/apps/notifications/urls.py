from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("notifications", views.NotificationViewSet, basename="notification")
router.register("notification-preferences", views.NotificationPreferenceViewSet, basename="notification-preference")
router.register("activity-feed", views.ActivityFeedViewSet, basename="activity-feed")

urlpatterns = [
    path("", include(router.urls)),
]
