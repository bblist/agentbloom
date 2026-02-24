from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ReceptionistConfigView,
    ChatSessionViewSet,
    ChatAnalyticsViewSet,
    WidgetConfigView,
    WidgetChatView,
)

router = DefaultRouter()
router.register(r"sessions", ChatSessionViewSet, basename="chat-session")
router.register(r"analytics", ChatAnalyticsViewSet, basename="chat-analytics")

urlpatterns = [
    path("config/", ReceptionistConfigView.as_view(), name="receptionist-config"),
    # Public widget endpoints
    path("widget/config/", WidgetConfigView.as_view(), name="widget-config"),
    path("widget/chat/", WidgetChatView.as_view(), name="widget-chat"),
] + router.urls
