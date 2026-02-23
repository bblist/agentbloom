import uuid
from django.db import models
from django.utils import timezone


class FeatureFlag(models.Model):
    """Feature flag for gradual rollouts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    rollout_percentage = models.IntegerField(default=0)  # 0-100
    target_plans = models.JSONField(default=list, blank=True)  # ["pro", "enterprise"]
    target_orgs = models.JSONField(default=list, blank=True)  # specific org IDs
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "feature_flags"

    def __str__(self):
        return f"{self.name} ({'ON' if self.is_enabled else 'OFF'})"


class FeatureFlagHistory(models.Model):
    """Track changes to feature flags."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flag = models.ForeignKey(FeatureFlag, on_delete=models.CASCADE, related_name="history")
    changed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    old_value = models.JSONField(default=dict)
    new_value = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "feature_flag_history"
        ordering = ["-created_at"]


class AdminAuditLog(models.Model):
    """Admin-specific audit trail."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100)
    target_id = models.UUIDField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "admin_audit_logs"
        ordering = ["-created_at"]


class SupportTicket(models.Model):
    """Support ticket from users."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("waiting", "Waiting on User"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="support_tickets")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="support_tickets")
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default="medium")
    category = models.CharField(max_length=100, blank=True)
    assigned_to = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="assigned_tickets")
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "support_tickets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.id} {self.subject} ({self.status})"


class SupportMessage(models.Model):
    """Message within a support ticket."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal note
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "support_messages"
        ordering = ["created_at"]


class ContentModerationQueue(models.Model):
    """Content flagged for review."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE)
    content_type = models.CharField(max_length=100)  # site, page, community_post
    content_id = models.UUIDField()
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="pending")
    reviewed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "content_moderation_queue"
        ordering = ["-created_at"]


class SystemHealthCheck(models.Model):
    """System health monitoring records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.CharField(max_length=100)  # database, redis, ses, stripe, llm
    status = models.CharField(max_length=50, choices=[
        ("healthy", "Healthy"),
        ("degraded", "Degraded"),
        ("down", "Down"),
    ])
    response_time_ms = models.IntegerField(default=0)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "system_health_checks"
        ordering = ["-created_at"]
