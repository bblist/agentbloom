import uuid
from django.db import models
from django.utils import timezone


class Site(models.Model):
    """A published website belonging to an organization."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="sites")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    custom_domain = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    template = models.ForeignKey("Template", on_delete=models.SET_NULL, null=True, blank=True)
    global_styles = models.JSONField(default=dict, blank=True)  # CSS variables, fonts
    seo_defaults = models.JSONField(default=dict, blank=True)
    favicon_url = models.URLField(blank=True)
    analytics_id = models.CharField(max_length=100, blank=True)  # GA4
    # Custom code injection zones
    head_code = models.TextField(blank=True)  # Custom HTML/JS in <head>
    body_start_code = models.TextField(blank=True)  # After opening <body>
    body_end_code = models.TextField(blank=True)  # Before closing </body>
    # PWA support
    is_pwa = models.BooleanField(default=False)
    pwa_manifest = models.JSONField(default=dict, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sites"
        unique_together = ("org", "slug")

    def __str__(self):
        return f"{self.name} ({self.org.name})"


class Page(models.Model):
    """A page within a site."""

    PAGE_TYPES = [
        ("page", "Standard Page"),
        ("blog_post", "Blog Post"),
        ("landing", "Landing Page"),
        ("legal", "Legal Page"),
        ("utility", "Utility Page"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="pages")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    path = models.CharField(max_length=500)  # e.g. /about, /services/hvac
    page_type = models.CharField(max_length=50, choices=PAGE_TYPES, default="page")
    is_homepage = models.BooleanField(default=False)
    content_blocks = models.JSONField(default=list)  # Block-based content
    # Per-page SEO
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    og_image_url = models.URLField(blank=True)
    canonical_url = models.URLField(blank=True)
    no_index = models.BooleanField(default=False)
    schema_markup = models.JSONField(default=dict, blank=True)  # Structured data
    # Per-page custom code
    custom_css = models.TextField(blank=True)
    custom_js = models.TextField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("draft", "Draft"), ("published", "Published"), ("scheduled", "Scheduled")],
        default="draft",
    )
    publish_at = models.DateTimeField(null=True, blank=True)  # Scheduled publishing
    sort_order = models.IntegerField(default=0)
    # Analytics
    view_count = models.IntegerField(default=0)
    unique_visitor_count = models.IntegerField(default=0)
    avg_time_on_page = models.IntegerField(default=0)  # seconds
    bounce_rate = models.FloatField(default=0)
    # Performance
    performance_score = models.IntegerField(null=True, blank=True)  # Lighthouse-style 0-100
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pages"
        unique_together = ("site", "slug")
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.title} — {self.site.name}"


class PageVersion(models.Model):
    """Version history for pages (rollback support)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    content_blocks = models.JSONField(default=list)
    diff_summary = models.TextField(blank=True)  # Human-readable diff description
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "page_versions"
        unique_together = ("page", "version_number")
        ordering = ["-version_number"]


class ABTest(models.Model):
    """A/B testing for pages — agent creates variants, system splits traffic."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("running", "Running"),
        ("paused", "Paused"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="ab_tests")
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    traffic_split = models.JSONField(default=dict)  # {variant_id: percentage}
    winning_variant = models.ForeignKey("ABTestVariant", on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="won_tests")
    target_metric = models.CharField(max_length=100, default="conversion")  # conversion, click, time_on_page
    min_sample_size = models.IntegerField(default=100)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "ab_tests"


class ABTestVariant(models.Model):
    """A variant in an A/B test."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(ABTest, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=255)  # "Control", "Variant A", etc.
    content_blocks = models.JSONField(default=list)
    impressions = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "ab_test_variants"

    @property
    def conversion_rate(self):
        return (self.conversions / self.impressions * 100) if self.impressions else 0


class BlogPost(models.Model):
    """Blog post — extends Page with blog-specific fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name="blog_post")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="blog_posts")
    author_name = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    excerpt = models.TextField(blank=True)
    featured_image_url = models.URLField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_featured = models.BooleanField(default=False)
    reading_time_minutes = models.IntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_posts"
        ordering = ["-published_at"]


class Popup(models.Model):
    """Popup / modal for lead capture — exit-intent, timed, scroll-triggered."""

    TRIGGER_TYPES = [
        ("exit_intent", "Exit Intent"),
        ("timed", "Time Delay"),
        ("scroll", "Scroll Percentage"),
        ("click", "Click Trigger"),
        ("page_load", "Page Load"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="popups")
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES, default="timed")
    trigger_config = models.JSONField(default=dict)  # {delay_seconds, scroll_pct, css_selector}
    content_blocks = models.JSONField(default=list)  # Block-based popup content
    target_pages = models.JSONField(default=list, blank=True)  # Page paths or "all"
    frequency = models.CharField(max_length=50, choices=[
        ("every_visit", "Every Visit"),
        ("once_per_session", "Once Per Session"),
        ("once_ever", "Once Ever"),
    ], default="once_per_session")
    is_active = models.BooleanField(default=True)
    impressions = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "popups"


class SiteBackup(models.Model):
    """Site backup for data protection and restore."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="backups")
    backup_url = models.URLField()  # S3 URL of backup archive
    size_bytes = models.BigIntegerField(default=0)
    pages_count = models.IntegerField(default=0)
    backup_type = models.CharField(max_length=50, choices=[
        ("auto", "Automatic"),
        ("manual", "Manual"),
        ("pre_deploy", "Pre-Deploy"),
    ], default="auto")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "site_backups"
        ordering = ["-created_at"]


class Template(models.Model):
    """Pre-built page template."""

    CATEGORY_CHOICES = [
        ("hvac", "HVAC"),
        ("restaurant", "Restaurant"),
        ("yoga", "Yoga / Fitness"),
        ("salon", "Salon / Spa"),
        ("dental", "Dental"),
        ("plumbing", "Plumbing"),
        ("legal", "Legal"),
        ("real_estate", "Real Estate"),
        ("photography", "Photography"),
        ("cleaning", "Cleaning"),
        ("general", "General"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="general")
    description = models.TextField(blank=True)
    preview_image_url = models.URLField(blank=True)
    preview_url = models.URLField(blank=True)
    default_pages = models.JSONField(default=list)  # Pre-configured page structures
    default_styles = models.JSONField(default=dict, blank=True)  # Theme defaults
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    # Usage analytics & ratings
    usage_count = models.IntegerField(default=0)
    avg_rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0)  # Avg conversion of sites using this template
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "templates"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} ({self.category})"


class TemplateRating(models.Model):
    """User rating for a template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "template_ratings"
        unique_together = ("template", "user")


class Component(models.Model):
    """Reusable UI component / block type."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.CharField(max_length=100)  # hero, cta, pricing, testimonials, etc.
    schema = models.JSONField(default=dict)  # Config schema for block
    default_props = models.JSONField(default=dict)  # Default values
    preview_image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "components"

    def __str__(self):
        return f"{self.name} ({self.category})"


class MediaLibrary(models.Model):
    """User-uploaded media files."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="media")
    filename = models.CharField(max_length=255)
    file_url = models.URLField()
    file_type = models.CharField(max_length=50)  # image, video, document
    mime_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()  # bytes
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    alt_text = models.CharField(max_length=500, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "media_library"
        ordering = ["-created_at"]
        verbose_name_plural = "Media library"

    def __str__(self):
        return self.filename


class Form(models.Model):
    """Dynamic form for a site (contact forms, lead capture, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="forms")
    name = models.CharField(max_length=255)
    fields_schema = models.JSONField(default=list)  # Field definitions
    # Multi-step & logic
    is_multi_step = models.BooleanField(default=False)
    steps = models.JSONField(default=list, blank=True)  # [{title, field_ids}]
    conditional_logic = models.JSONField(default=list, blank=True)  # [{if_field, condition, then_show}]
    redirect_url = models.URLField(blank=True)
    success_message = models.TextField(default="Thank you for your submission!")
    notify_email = models.EmailField(blank=True)  # Where to send notifications
    # Spam protection
    honeypot_enabled = models.BooleanField(default=True)
    recaptcha_enabled = models.BooleanField(default=False)
    # Webhook forwarding
    webhook_url = models.URLField(blank=True)  # Forward submissions to Zapier/Make/etc.
    webhook_headers = models.JSONField(default=dict, blank=True)
    # File uploads
    allow_file_upload = models.BooleanField(default=False)
    max_file_size_mb = models.IntegerField(default=10)
    allowed_file_types = models.JSONField(default=list, blank=True)  # ["pdf", "jpg", "png"]
    is_active = models.BooleanField(default=True)
    submission_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "forms"

    def __str__(self):
        return f"{self.name} — {self.site.name}"


class FormSubmission(models.Model):
    """Submitted data from a form."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions")
    data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "form_submissions"
        ordering = ["-created_at"]


class SiteNavigation(models.Model):
    """Navigation menu structure for a site."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="navigation")
    location = models.CharField(max_length=50, choices=[
        ("header", "Header"),
        ("footer", "Footer"),
        ("sidebar", "Sidebar"),
    ])
    items = models.JSONField(default=list)  # [{label, url, children}]
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "site_navigation"
        unique_together = ("site", "location")
