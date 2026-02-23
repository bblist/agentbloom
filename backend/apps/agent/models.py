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
    llm_provider = models.CharField(max_length=50, default="openai")  # openai, claude, gemini
    llm_model = models.CharField(max_length=100, default="gpt-4o")
    fallback_provider = models.CharField(max_length=50, default="claude")
    fallback_model = models.CharField(max_length=100, default="claude-4.6")
    design_provider = models.CharField(max_length=50, default="gemini")
    design_model = models.CharField(max_length=100, default="gemini-3.2-pro")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=4096)
    knowledge_base_enabled = models.BooleanField(default=True)
    # Rate limiting / token budgets
    token_budget_daily = models.IntegerField(default=100000)
    token_budget_monthly = models.IntegerField(default=2000000)
    tokens_used_today = models.IntegerField(default=0)
    tokens_used_month = models.IntegerField(default=0)
    # Confidence & behavior
    confidence_threshold = models.FloatField(default=0.7)  # Below this → ask clarification
    auto_approve_actions = models.BooleanField(default=False)  # If False → approval queue
    debug_mode = models.BooleanField(default=False)  # Show reasoning steps to user
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
    # Context window management
    summary = models.TextField(blank=True)  # Auto-summarized context for long conversations
    total_tokens = models.IntegerField(default=0)
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
    # Confidence scoring
    confidence_score = models.FloatField(null=True, blank=True)  # 0.0–1.0
    # Branching / undo
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="branches")
    is_undone = models.BooleanField(default=False)  # Soft-undo
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:80]}"


class ConversationStateSnapshot(models.Model):
    """State snapshot for undo/rollback support in conversations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="snapshots")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="snapshot")
    state_data = models.JSONField(default=dict)  # Serialized state at this point
    label = models.CharField(max_length=255, blank=True)  # e.g. "Before page redesign"
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "conversation_state_snapshots"
        ordering = ["-created_at"]


class AgentApprovalQueue(models.Model):
    """Action approval workflow — agent proposes, user approves/rejects."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="approval_queue")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="approvals")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)  # publish_page, send_email, create_booking, etc.
    action_description = models.TextField()
    action_data = models.JSONField(default=dict)  # Tool args that would be executed
    preview_data = models.JSONField(default=dict, blank=True)  # Preview/diff for user
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "agent_approval_queue"
        ordering = ["-created_at"]


class AgentLearning(models.Model):
    """Agent learning from user corrections — stores preferences for future use."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="agent_learnings")
    category = models.CharField(max_length=100)  # style, tone, content, design, etc.
    original_output = models.TextField()
    corrected_output = models.TextField()
    user_feedback = models.TextField(blank=True)
    context = models.JSONField(default=dict, blank=True)  # What was the agent doing
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "agent_learnings"
        ordering = ["-created_at"]


class ToolVersion(models.Model):
    """Versioned tool definitions for the agent tool registry."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)  # e.g. "generate_page"
    version = models.CharField(max_length=20)  # e.g. "v1", "v2"
    description = models.TextField()
    parameters_schema = models.JSONField(default=dict)  # JSON schema for args
    return_schema = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    deprecated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "tool_versions"
        unique_together = ("name", "version")
        ordering = ["name", "-version"]

    def __str__(self):
        return f"{self.name} {self.version}"


class PromptCache(models.Model):
    """Cache for system prompts and KB context to reduce token usage."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="prompt_cache")
    cache_key = models.CharField(max_length=255)  # Hash of prompt content
    content = models.TextField()
    token_count = models.IntegerField(default=0)
    hit_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "prompt_cache"
        unique_together = ("org", "cache_key")


class ScheduledTask(models.Model):
    """Agent-scheduled task (e.g., "send email tomorrow at 9am", "every Monday send report")."""

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
    # Recurring support
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=255, blank=True)  # RRULE format
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    run_count = models.IntegerField(default=0)
    max_runs = models.IntegerField(default=0)  # 0 = unlimited
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
