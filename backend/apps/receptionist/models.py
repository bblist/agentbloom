"""
AI Receptionist Models

Web chat widget + configuration for the embeddable AI receptionist.
Voice/SMS support disabled by default (Phase 11 add-on).
"""

import uuid

from django.conf import settings
from django.db import models


class ReceptionistConfig(models.Model):
    """Per-org configuration for the AI receptionist."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.OneToOneField(
        "users.Organization", on_delete=models.CASCADE, related_name="receptionist_config"
    )
    is_active = models.BooleanField(default=False)

    # Persona
    persona_name = models.CharField(max_length=100, default="Assistant")
    greeting_message = models.TextField(
        default="Hello! How can I help you today?"
    )
    avatar_url = models.URLField(blank=True, default="")

    # Appearance
    primary_color = models.CharField(max_length=7, default="#2563EB")  # blue-600
    position = models.CharField(
        max_length=20,
        choices=[("bottom-right", "Bottom Right"), ("bottom-left", "Bottom Left")],
        default="bottom-right",
    )

    # Business hours (JSON: {"mon": {"start": "09:00", "end": "17:00"}, ...})
    business_hours = models.JSONField(default=dict, blank=True)
    after_hours_message = models.TextField(
        default="We're currently closed. Please leave a message and we'll get back to you."
    )

    # Behavior
    language = models.CharField(max_length=10, default="en")
    max_ai_turns = models.IntegerField(default=10)
    escalation_keywords = models.JSONField(
        default=list, blank=True,
        help_text='Keywords that trigger human handoff, e.g. ["emergency", "urgent"]',
    )
    custom_instructions = models.TextField(
        blank=True, default="",
        help_text="Additional instructions for the AI receptionist persona.",
    )

    # Capabilities
    can_book_appointments = models.BooleanField(default=True)
    can_collect_leads = models.BooleanField(default=True)
    can_answer_faq = models.BooleanField(default=True)

    # Widget embed key (used in JS snippet)
    embed_key = models.CharField(max_length=64, unique=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "receptionist_configs"

    def __str__(self):
        return f"Receptionist: {self.org.name}"

    def save(self, *args, **kwargs):
        if not self.embed_key:
            self.embed_key = uuid.uuid4().hex
        super().save(*args, **kwargs)


class ChatSession(models.Model):
    """A single chat session with a website visitor."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(
        "users.Organization", on_delete=models.CASCADE, related_name="chat_sessions"
    )
    visitor_id = models.CharField(max_length=255, blank=True, default="")
    visitor_name = models.CharField(max_length=255, blank=True, default="")
    visitor_email = models.EmailField(blank=True, default="")

    STATUS_CHOICES = [
        ("active", "Active"),
        ("closed", "Closed"),
        ("transferred", "Transferred to Human"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    CHANNEL_CHOICES = [("web", "Web Chat"), ("sms", "SMS")]
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="web")

    sentiment_score = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    actions_taken = models.JSONField(default=list, blank=True)
    source_url = models.URLField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chat_sessions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["org", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Chat {self.id} ({self.status})"


class ChatMessage(models.Model):
    """Individual message in a chat session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )

    ROLE_CHOICES = [
        ("visitor", "Visitor"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class ChatAnalytics(models.Model):
    """Daily aggregated chat analytics per org."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(
        "users.Organization", on_delete=models.CASCADE, related_name="chat_analytics"
    )
    date = models.DateField()
    total_sessions = models.IntegerField(default=0)
    ai_resolved = models.IntegerField(default=0)
    transferred = models.IntegerField(default=0)
    leads_collected = models.IntegerField(default=0)
    appointments_booked = models.IntegerField(default=0)
    avg_messages_per_session = models.DecimalField(
        max_digits=5, decimal_places=1, default=0
    )
    avg_sentiment = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    top_queries = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "chat_analytics"
        unique_together = ("org", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"Analytics {self.org.name} — {self.date}"
