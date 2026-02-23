import uuid
from django.db import models
from django.utils import timezone


class SEOSettings(models.Model):
    """Per-site SEO configuration."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.OneToOneField("sites.Site", on_delete=models.CASCADE, related_name="seo_settings")
    auto_seo_enabled = models.BooleanField(default=True)
    schema_markup_enabled = models.BooleanField(default=True)
    schema_types = models.JSONField(default=list, blank=True)  # ["LocalBusiness", "Organization", ...]
    sitemap_enabled = models.BooleanField(default=True)
    robots_txt = models.TextField(blank=True, default="User-agent: *\nAllow: /")
    google_analytics_id = models.CharField(max_length=100, blank=True)
    google_search_console_verified = models.BooleanField(default=False)
    local_seo_enabled = models.BooleanField(default=False)
    business_name = models.CharField(max_length=255, blank=True)
    business_address = models.JSONField(default=dict, blank=True)
    business_phone = models.CharField(max_length=50, blank=True)
    business_hours = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "seo_settings"
        verbose_name = "SEO Settings"
        verbose_name_plural = "SEO Settings"


class SEOAudit(models.Model):
    """Periodic SEO audit results."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey("sites.Site", on_delete=models.CASCADE, related_name="seo_audits")
    score = models.IntegerField(default=0)  # 0-100
    issues = models.JSONField(default=list)  # [{type, severity, page, description, fix}]
    recommendations = models.JSONField(default=list)
    page_scores = models.JSONField(default=dict)  # {page_id: score}
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "seo_audits"
        ordering = ["-created_at"]


class TrackedKeyword(models.Model):
    """Keyword rank tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey("sites.Site", on_delete=models.CASCADE, related_name="tracked_keywords")
    keyword = models.CharField(max_length=255)
    current_rank = models.IntegerField(null=True, blank=True)
    previous_rank = models.IntegerField(null=True, blank=True)
    best_rank = models.IntegerField(null=True, blank=True)
    search_volume = models.IntegerField(null=True, blank=True)
    difficulty = models.IntegerField(null=True, blank=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    history = models.JSONField(default=list, blank=True)  # [{date, rank}]
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "tracked_keywords"
        unique_together = ("site", "keyword")


class GoogleConnection(models.Model):
    """Google Search Console / Analytics OAuth connection."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="google_connections")
    service = models.CharField(max_length=50, choices=[
        ("search_console", "Search Console"),
        ("analytics", "Google Analytics"),
    ])
    property_url = models.URLField(blank=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "google_connections"
