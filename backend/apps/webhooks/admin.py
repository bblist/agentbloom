from django.contrib import admin
from .models import WebhookEndpoint, WebhookEvent, WebhookDeliveryLog, IncomingWebhook


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "is_active", "total_deliveries", "total_failures", "last_triggered_at")
    list_filter = ("is_active",)
    search_fields = ("name", "url")


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "category", "is_active")
    list_filter = ("category", "is_active")


@admin.register(WebhookDeliveryLog)
class WebhookDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "event_type", "status_code", "success", "attempt_number", "created_at")
    list_filter = ("success", "event_type")


@admin.register(IncomingWebhook)
class IncomingWebhookAdmin(admin.ModelAdmin):
    list_display = ("source", "event_type", "processed", "signature_valid", "created_at")
    list_filter = ("source", "processed")
