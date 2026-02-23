import uuid
from django.db import models
from django.utils import timezone
from pgvector.django import VectorField


class KBDocument(models.Model):
    """Uploaded knowledge base document."""

    SOURCE_TYPES = [
        ("upload", "File Upload"),
        ("url", "URL Scrape"),
        ("text", "Manual Text"),
        ("gbp", "Google Business Profile"),
        ("faq", "Auto-Generated FAQ"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="kb_documents")
    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, default="upload")
    source_url = models.URLField(blank=True)
    file_url = models.URLField(blank=True)
    file_type = models.CharField(max_length=50, blank=True)  # pdf, docx, txt, csv, etc.
    raw_text = models.TextField(blank=True)
    chunk_count = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "kb_documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.source_type})"


class KBChunk(models.Model):
    """Text chunk with vector embedding for semantic search."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(KBDocument, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    chunk_index = models.IntegerField(default=0)
    embedding = VectorField(dimensions=1536, null=True, blank=True)  # OpenAI text-embedding-3-small
    token_count = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)  # page number, section title, etc.
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "kb_chunks"
        ordering = ["chunk_index"]
        indexes = [
            # pgvector HNSW index created via migration
        ]

    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.title}"


class KBScrapeSchedule(models.Model):
    """Scheduled URL scraping for keeping docs up to date."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="scrape_schedules")
    url = models.URLField()
    frequency = models.CharField(max_length=50, choices=[
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ], default="weekly")
    last_scraped = models.DateTimeField(null=True, blank=True)
    next_scrape = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "kb_scrape_schedules"


class GBPConnection(models.Model):
    """Google Business Profile connection for importing reviews, info, etc."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="gbp_connections")
    place_id = models.CharField(max_length=255)
    business_name = models.CharField(max_length=255)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "gbp_connections"
