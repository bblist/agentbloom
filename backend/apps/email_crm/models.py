import uuid
from django.db import models
from django.utils import timezone


class Contact(models.Model):
    """CRM contact / lead."""

    SOURCE_CHOICES = [
        ("manual", "Manual"),
        ("form", "Form Submission"),
        ("import", "CSV Import"),
        ("agent", "AI Agent"),
        ("booking", "Booking"),
        ("purchase", "Purchase"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="contacts")
    email = models.EmailField()
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="manual")
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    lead_score = models.IntegerField(default=0)
    is_subscribed = models.BooleanField(default=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    # Lifecycle
    lifecycle_stage = models.CharField(max_length=50, choices=[
        ("subscriber", "Subscriber"),
        ("lead", "Lead"),
        ("marketing_qualified", "Marketing Qualified"),
        ("sales_qualified", "Sales Qualified"),
        ("opportunity", "Opportunity"),
        ("customer", "Customer"),
        ("evangelist", "Evangelist"),
    ], default="subscriber")
    # Communication preferences
    sms_subscribed = models.BooleanField(default=False)
    sms_phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contacts"
        unique_together = ("org", "email")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["org", "lead_score"]),
            models.Index(fields=["org", "source"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Segment(models.Model):
    """Dynamic or static contact segment."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="segments")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_dynamic = models.BooleanField(default=True)
    filter_rules = models.JSONField(default=list, blank=True)  # Dynamic segment rules
    static_contacts = models.ManyToManyField(Contact, blank=True, related_name="static_segments")
    contact_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "segments"

    def __str__(self):
        return f"{self.name} ({self.contact_count})"


class EmailTemplate(models.Model):
    """Reusable email template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="email_templates")
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=500)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    variables = models.JSONField(default=list, blank=True)  # Available merge tags
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "email_templates"

    def __str__(self):
        return self.name


class Campaign(models.Model):
    """Email campaign."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=500)
    from_name = models.CharField(max_length=255)
    from_email = models.EmailField()
    reply_to = models.EmailField(blank=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    segment = models.ForeignKey(Segment, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Stats
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_opens = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    total_bounces = models.IntegerField(default=0)
    total_complaints = models.IntegerField(default=0)
    total_unsubscribes = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campaigns"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def open_rate(self):
        return (self.total_opens / self.total_delivered * 100) if self.total_delivered else 0

    @property
    def click_rate(self):
        return (self.total_clicks / self.total_delivered * 100) if self.total_delivered else 0


class CampaignEvent(models.Model):
    """Individual email event (delivery, open, click, bounce, etc.)."""

    EVENT_TYPES = [
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("opened", "Opened"),
        ("clicked", "Clicked"),
        ("bounced", "Bounced"),
        ("complained", "Complained"),
        ("unsubscribed", "Unsubscribed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="events")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="campaign_events")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    metadata = models.JSONField(default=dict, blank=True)  # link clicked, bounce reason, etc.
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "campaign_events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["campaign", "event_type"]),
        ]


class Automation(models.Model):
    """Email automation / drip sequence."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="automations")
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=100)  # form_submit, tag_added, booking, purchase
    trigger_config = models.JSONField(default=dict, blank=True)
    steps = models.JSONField(default=list)  # [{type: "email"/"delay"/"condition", config: {}}]
    is_active = models.BooleanField(default=False)
    enrolled_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "automations"

    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'paused'})"


class AutomationEnrollment(models.Model):
    """Contact enrolled in an automation."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paused", "Paused"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name="enrollments")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="automations")
    current_step = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="active")
    next_action_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "automation_enrollments"
        unique_together = ("automation", "contact")


class Deal(models.Model):
    """CRM deal / opportunity."""

    STAGE_CHOICES = [
        ("lead", "Lead"),
        ("qualified", "Qualified"),
        ("proposal", "Proposal"),
        ("negotiation", "Negotiation"),
        ("won", "Won"),
        ("lost", "Lost"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="deals")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="deals")
    title = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default="lead")
    probability = models.IntegerField(default=0)  # 0-100
    expected_close_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "deals"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — ${self.value} ({self.stage})"


class ScoringRule(models.Model):
    """Lead scoring rule."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="scoring_rules")
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)  # email_open, form_submit, page_visit, etc.
    condition = models.JSONField(default=dict, blank=True)
    points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "scoring_rules"

    def __str__(self):
        return f"{self.name} (+{self.points} pts)"


class ContactActivity(models.Model):
    """Unified activity timeline for a contact — all interactions in one place."""

    ACTIVITY_TYPES = [
        ("email_sent", "Email Sent"),
        ("email_opened", "Email Opened"),
        ("email_clicked", "Email Clicked"),
        ("form_submitted", "Form Submitted"),
        ("page_visited", "Page Visited"),
        ("booking_made", "Booking Made"),
        ("purchase", "Purchase Made"),
        ("call", "Phone Call"),
        ("sms_sent", "SMS Sent"),
        ("sms_received", "SMS Received"),
        ("note", "Manual Note"),
        ("tag_added", "Tag Added"),
        ("deal_stage_changed", "Deal Stage Changed"),
        ("enrolled", "Enrolled in Course"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # Extra context per type
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "contact_activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["contact", "-created_at"]),
        ]


class EmailABTest(models.Model):
    """A/B test for email campaigns — subject line, content, or send time."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name="ab_test")
    test_type = models.CharField(max_length=50, choices=[
        ("subject", "Subject Line"),
        ("content", "Content"),
        ("send_time", "Send Time"),
    ])
    variant_a = models.JSONField(default=dict)  # {subject: "...", html_content: "..."}
    variant_b = models.JSONField(default=dict)
    sample_size_pct = models.IntegerField(default=20)  # % of list to test on
    winning_metric = models.CharField(max_length=50, default="open_rate")  # open_rate, click_rate
    winner = models.CharField(max_length=1, blank=True)  # "a" or "b"
    results_a = models.JSONField(default=dict, blank=True)
    results_b = models.JSONField(default=dict, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "email_ab_tests"


class DeliverabilityMetrics(models.Model):
    """SES deliverability tracking — reputation, bounce/complaint rates, warmup progress."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="deliverability_metrics")
    date = models.DateField()
    emails_sent = models.IntegerField(default=0)
    delivered = models.IntegerField(default=0)
    bounced = models.IntegerField(default=0)
    complaints = models.IntegerField(default=0)
    bounce_rate = models.FloatField(default=0)
    complaint_rate = models.FloatField(default=0)
    reputation_score = models.IntegerField(default=100)  # 0-100
    # Warmup tracking
    is_warming = models.BooleanField(default=False)
    warmup_day = models.IntegerField(default=0)
    daily_limit = models.IntegerField(default=50)  # Starts low, ramps up
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "deliverability_metrics"
        unique_together = ("org", "date")
        ordering = ["-date"]


class SMSCampaign(models.Model):
    """SMS marketing campaign."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("sending", "Sending"),
        ("sent", "Sent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="sms_campaigns")
    name = models.CharField(max_length=255)
    message = models.TextField(max_length=1600)  # SMS max length
    segment = models.ForeignKey(Segment, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "sms_campaigns"
        ordering = ["-created_at"]
