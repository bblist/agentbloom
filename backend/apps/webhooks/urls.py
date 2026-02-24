from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("endpoints", views.WebhookEndpointViewSet, basename="webhook-endpoint")
router.register("events", views.WebhookEventViewSet, basename="webhook-event")
router.register("logs", views.WebhookDeliveryLogViewSet, basename="webhook-log")

urlpatterns = [
    path("", include(router.urls)),
    path("incoming/<str:source>/", views.incoming_webhook, name="incoming-webhook"),
]
