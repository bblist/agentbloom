import uuid
import hmac
import hashlib
from django.db import models
from django.utils import timezone


class WebhookEndpoint(models.Model):
    """User-configured webhook endpoint (like Zapier/Make integration)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="webhook_endpoints")
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=1000)
    secret = models.CharField(max_length=255, blank=True)  # HMAC signing secret
    is_active = models.BooleanField(default=True)
    # Which events to subscribe to
    events = models.JSONField(default=list)
    # ["site.published", "booking.created", "payment.completed", "contact.created", ...]
    headers = models.JSONField(default=dict, blank=True)  # Custom headers to send
    # Retry config
    max_retries = models.IntegerField(default=3)
    retry_interval_seconds = models.IntegerField(default=60)
    # Stats
    total_deliveries = models.IntegerField(default=0)
    total_failures = models.IntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    last_status_code = models.IntegerField(null=True, blank=True)
    # Disabled after repeated failures
    consecutive_failures = models.IntegerField(default=0)
    auto_disabled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "webhook_endpoints"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} → {self.url}"

    def sign_payload(self, payload: str) -> str:
        """Generate HMAC-SHA256 signature for the payload."""
        if not self.secret:
            return ""
        return hmac.new(
            self.secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()


class WebhookEvent(models.Model):
    """Registered webhook event type."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=255, unique=True)
    # e.g. "site.published", "booking.created", "contact.tag_added"
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)  # site, booking, payment, etc.
    payload_schema = models.JSONField(default=dict, blank=True)  # JSON Schema of event payload
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "webhook_events"
        ordering = ["event_type"]

    def __str__(self):
        return self.event_type


class WebhookDeliveryLog(models.Model):
    """Log of every webhook delivery attempt."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name="delivery_logs")
    event_type = models.CharField(max_length=255)
    payload = models.JSONField(default=dict)
    # Request details
    request_headers = models.JSONField(default=dict, blank=True)
    # Response
    status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    response_headers = models.JSONField(default=dict, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    # Delivery state
    success = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1)
    error_message = models.TextField(blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "webhook_delivery_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["endpoint", "-created_at"]),
            models.Index(fields=["event_type", "-created_at"]),
        ]


class IncomingWebhook(models.Model):
    """Incoming webhooks FROM external services (Stripe, SES, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=100)  # stripe, ses, google, zapier
    event_type = models.CharField(max_length=255)
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict, blank=True)
    signature_valid = models.BooleanField(null=True, blank=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "incoming_webhooks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["source", "event_type"]),
            models.Index(fields=["processed", "-created_at"]),
        ]
