import uuid
from django.db import models
from django.utils import timezone


class AgentConfig(models.Model):
    """Per-org agent configuration — tone, persona, tools enabled, etc."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.OneToOneField("users.Organization", on_delete=models.CASCADE, related_name="agent_config")
    display_name = models.CharField(max_length=255, default="AI Assistant")
    persona = models.TextField(
        default="You are a helpful business assistant. Be friendly, professional, and concise."
    )
    tone = models.CharField(
        max_length=50,
        choices=[
            ("professional", "Professional"),
            ("friendly", "Friendly"),
            ("casual", "Casual"),
            ("formal", "Formal"),
        ],
        default="friendly",
    )
    enabled_tools = models.JSONField(default=list, blank=True)  # ["page_builder", "email_send", ...]
    llm_provider = models.CharField(max_length=50, default="gemini")  # gemini, claude
    llm_model = models.CharField(max_length=100, default="gemini-2.0-flash")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=4096)
    knowledge_base_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "agent_configs"

    def __str__(self):
        return f"Agent config for {self.org.name}"


class Conversation(models.Model):
    """A conversation thread between user and agent."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="conversations")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=255, default="New Conversation")
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.user.email})"


class Message(models.Model):
    """Individual message in a conversation."""

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
        ("tool", "Tool"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tool_name = models.CharField(max_length=100, blank=True)  # For tool messages
    tool_args = models.JSONField(default=dict, blank=True)
    tool_result = models.JSONField(default=dict, blank=True)
    token_count = models.IntegerField(default=0)
    model_used = models.CharField(max_length=100, blank=True)
    latency_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:80]}"


class ScheduledTask(models.Model):
    """Agent-scheduled task (e.g., "send email tomorrow at 9am")."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="scheduled_tasks")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="scheduled_tasks")
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, related_name="scheduled_tasks")
    tool_name = models.CharField(max_length=100)
    tool_args = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "scheduled_tasks"
        ordering = ["scheduled_for"]

    def __str__(self):
        return f"{self.tool_name} @ {self.scheduled_for}"
