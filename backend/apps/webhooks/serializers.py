from rest_framework import serializers
from .models import WebhookEndpoint, WebhookEvent, WebhookDeliveryLog


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = "__all__"
        read_only_fields = ("id", "org", "total_deliveries", "total_failures", "last_triggered_at",
                            "consecutive_failures", "auto_disabled_at", "created_at", "updated_at")
        extra_kwargs = {"secret": {"write_only": True}}


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = "__all__"
        read_only_fields = ("id",)


class WebhookDeliveryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDeliveryLog
        fields = "__all__"
        read_only_fields = ("id", "created_at")
