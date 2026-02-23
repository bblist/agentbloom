from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"conversations", views.ConversationViewSet, basename="conversation")
router.register(r"tasks", views.ScheduledTaskViewSet, basename="scheduled-task")

urlpatterns = [
    path("config/", views.AgentConfigView.as_view(), name="agent-config"),
    path("chat/", views.ChatView.as_view(), name="agent-chat"),
    path("", include(router.urls)),
]
