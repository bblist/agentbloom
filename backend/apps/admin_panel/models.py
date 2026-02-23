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


class ImpersonationSession(models.Model):
    """Track admin impersonation of user accounts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="impersonation_sessions")
    target_user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="impersonated_sessions")
    reason = models.TextField()
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    actions_taken = models.JSONField(default=list, blank=True)  # [{action, timestamp, details}]
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "impersonation_sessions"
        ordering = ["-started_at"]


class UserLifecycleEvent(models.Model):
    """Track user lifecycle state transitions for admin overview."""

    STAGE_CHOICES = [
        ("signup", "Signed Up"),
        ("onboarding", "Onboarding"),
        ("activated", "Activated"),
        ("engaged", "Engaged"),
        ("at_risk", "At Risk"),
        ("churned", "Churned"),
        ("reactivated", "Reactivated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="lifecycle_events")
    from_stage = models.CharField(max_length=50, choices=STAGE_CHOICES, blank=True)
    to_stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    trigger = models.CharField(max_length=255, blank=True)  # What caused transition
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_lifecycle_events"
        ordering = ["-created_at"]


class RevenueAnalytics(models.Model):
    """Aggregated revenue analytics for admin dashboard (monthly snapshots)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    period_start = models.DateField()
    period_end = models.DateField()
    mrr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    arr = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    new_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    churned_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expansion_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_revenue_churn_rate = models.FloatField(default=0)  # %
    logo_churn_rate = models.FloatField(default=0)  # %
    ltv = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arpu = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    churned_customers = models.IntegerField(default=0)
    trial_to_paid_rate = models.FloatField(default=0)  # %
    # Cohort data
    cohort_data = models.JSONField(default=dict, blank=True)  # {cohort_month: {month_n: retention_pct}}
    plan_breakdown = models.JSONField(default=dict, blank=True)  # {plan_name: {count, revenue}}
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "revenue_analytics"
        ordering = ["-period_start"]
        unique_together = ("period_start", "period_end")


class PlatformMetrics(models.Model):
    """Daily platform-wide usage metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)  # DAU
    new_signups = models.IntegerField(default=0)
    total_sites = models.IntegerField(default=0)
    total_pages_published = models.IntegerField(default=0)
    total_agent_conversations = models.IntegerField(default=0)
    total_agent_tokens = models.BigIntegerField(default=0)
    total_emails_sent = models.IntegerField(default=0)
    total_bookings = models.IntegerField(default=0)
    total_courses_active = models.IntegerField(default=0)
    total_api_requests = models.IntegerField(default=0)
    avg_response_time_ms = models.IntegerField(default=0)
    error_rate = models.FloatField(default=0)  # %
    storage_used_gb = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "platform_metrics"
        ordering = ["-date"]
