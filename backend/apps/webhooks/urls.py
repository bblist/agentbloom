from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("webhook-endpoints", views.WebhookEndpointViewSet, basename="webhook-endpoint")
router.register("webhook-events", views.WebhookEventViewSet, basename="webhook-event")
router.register("webhook-logs", views.WebhookDeliveryLogViewSet, basename="webhook-log")

urlpatterns = [
    path("", include(router.urls)),
    path("incoming/<str:source>/", views.incoming_webhook, name="incoming-webhook"),
]
