import uuid
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """User notification — in-app, push, or email digest."""

    CHANNEL_CHOICES = [
        ("in_app", "In-App"),
        ("push", "Push (Web/Mobile)"),
        ("email", "Email"),
        ("sms", "SMS"),
    ]
    CATEGORY_CHOICES = [
        ("agent", "Agent"),
        ("site", "Site Builder"),
        ("course", "Course"),
        ("booking", "Booking"),
        ("payment", "Payment"),
        ("email_campaign", "Email Campaign"),
        ("support", "Support"),
        ("system", "System"),
        ("community", "Community"),
        ("security", "Security"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notifications")
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, null=True, blank=True)
    channel = models.CharField(max_length=50, choices=CHANNEL_CHOICES, default="in_app")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="system")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)  # Icon name or URL
    action_url = models.CharField(max_length=500, blank=True)  # Click-through URL
    action_label = models.CharField(max_length=100, blank=True)
    # Read/dismiss state
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_dismissed = models.BooleanField(default=False)
    # Delivery
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Grouping
    group_key = models.CharField(max_length=255, blank=True)  # Group related notifications
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["user", "channel"]),
        ]

    def __str__(self):
        return f"{self.title} → {self.user}"

    def mark_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])


class NotificationPreference(models.Model):
    """Per-user, per-category notification channel preferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notification_preferences")
    category = models.CharField(max_length=50, choices=Notification.CATEGORY_CHOICES)
    in_app = models.BooleanField(default=True)
    email = models.BooleanField(default=True)
    push = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)
    # Email digest grouping
    email_digest = models.CharField(max_length=50, choices=[
        ("immediate", "Immediate"),
        ("hourly", "Hourly Digest"),
        ("daily", "Daily Digest"),
        ("weekly", "Weekly Digest"),
        ("none", "None"),
    ], default="immediate")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_preferences"
        unique_together = ("user", "category")


class PushSubscription(models.Model):
    """Web Push / FCM subscription for a user device."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.URLField(max_length=1000)
    p256dh_key = models.CharField(max_length=500)
    auth_key = models.CharField(max_length=500)
    user_agent = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "push_subscriptions"


class ActivityFeedEntry(models.Model):
    """Organization-wide activity feed (timeline)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="activity_feed")
    actor = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    verb = models.CharField(max_length=100)  # "published", "enrolled", "booked", "sent_campaign"
    target_type = models.CharField(max_length=100, blank=True)  # "page", "course", "campaign"
    target_id = models.UUIDField(null=True, blank=True)
    target_title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "activity_feed"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["org", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.actor} {self.verb} {self.target_title}"
