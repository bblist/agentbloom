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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="pages")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    path = models.CharField(max_length=500)  # e.g. /about, /services/hvac
    is_homepage = models.BooleanField(default=False)
    content_blocks = models.JSONField(default=list)  # Block-based content
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    og_image_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=50,
        choices=[("draft", "Draft"), ("published", "Published")],
        default="draft",
    )
    sort_order = models.IntegerField(default=0)
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
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "page_versions"
        unique_together = ("page", "version_number")
        ordering = ["-version_number"]


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
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "templates"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} ({self.category})"


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
    redirect_url = models.URLField(blank=True)
    success_message = models.TextField(default="Thank you for your submission!")
    notify_email = models.EmailField(blank=True)  # Where to send notifications
    is_active = models.BooleanField(default=True)
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
