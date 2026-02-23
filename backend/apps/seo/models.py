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
    sitemap_url = models.URLField(blank=True)  # Generated sitemap URL
    sitemap_last_generated = models.DateTimeField(null=True, blank=True)
    robots_txt = models.TextField(blank=True, default="User-agent: *\nAllow: /")
    google_analytics_id = models.CharField(max_length=100, blank=True)
    google_search_console_verified = models.BooleanField(default=False)
    # Local SEO
    local_seo_enabled = models.BooleanField(default=False)
    business_name = models.CharField(max_length=255, blank=True)
    business_address = models.JSONField(default=dict, blank=True)
    business_phone = models.CharField(max_length=50, blank=True)
    business_hours = models.JSONField(default=dict, blank=True)
    service_area = models.JSONField(default=list, blank=True)  # Zip codes or city names
    # AI search readiness
    ai_search_optimization = models.BooleanField(default=True)  # Format for LLM consumption
    entity_markup_enabled = models.BooleanField(default=True)
    # Page speed config
    auto_image_optimization = models.BooleanField(default=True)  # WebP/AVIF conversion
    lazy_loading_enabled = models.BooleanField(default=True)
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
    # Breakdown scores
    technical_score = models.IntegerField(default=0)
    content_score = models.IntegerField(default=0)
    performance_score = models.IntegerField(default=0)
    accessibility_score = models.IntegerField(default=0)
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
    # Mapped page
    ranking_page = models.ForeignKey("sites.Page", on_delete=models.SET_NULL, null=True, blank=True)
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


class InternalLinkSuggestion(models.Model):
    """AI-generated internal linking suggestions between pages."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey("sites.Site", on_delete=models.CASCADE, related_name="link_suggestions")
    source_page = models.ForeignKey("sites.Page", on_delete=models.CASCADE, related_name="outbound_suggestions")
    target_page = models.ForeignKey("sites.Page", on_delete=models.CASCADE, related_name="inbound_suggestions")
    anchor_text = models.CharField(max_length=255)
    context = models.TextField(blank=True)  # Where in the source page to add the link
    confidence = models.FloatField(default=0)  # 0-1
    status = models.CharField(max_length=50, choices=[
        ("suggested", "Suggested"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ], default="suggested")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "internal_link_suggestions"
        ordering = ["-confidence"]


class PageSpeedMetrics(models.Model):
    """Core Web Vitals and page speed metrics per page."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey("sites.Page", on_delete=models.CASCADE, related_name="speed_metrics")
    # Core Web Vitals
    lcp = models.FloatField(null=True, blank=True)  # Largest Contentful Paint (seconds)
    fid = models.FloatField(null=True, blank=True)  # First Input Delay (ms)
    cls = models.FloatField(null=True, blank=True)  # Cumulative Layout Shift
    inp = models.FloatField(null=True, blank=True)  # Interaction to Next Paint (ms)
    ttfb = models.FloatField(null=True, blank=True)  # Time to First Byte (ms)
    # Scores
    performance_score = models.IntegerField(null=True, blank=True)  # 0-100
    seo_score = models.IntegerField(null=True, blank=True)
    accessibility_score = models.IntegerField(null=True, blank=True)
    best_practices_score = models.IntegerField(null=True, blank=True)
    # Page size
    total_size_kb = models.IntegerField(default=0)
    image_size_kb = models.IntegerField(default=0)
    js_size_kb = models.IntegerField(default=0)
    css_size_kb = models.IntegerField(default=0)
    measured_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "page_speed_metrics"
        ordering = ["-measured_at"]
