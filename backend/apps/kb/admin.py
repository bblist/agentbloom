from django.contrib import admin
from .models import KBDocument, KBChunk, KBScrapeSchedule, GBPConnection


@admin.register(KBDocument)
class KBDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "org", "source_type", "status", "chunk_count", "created_at")
    list_filter = ("source_type", "status")


@admin.register(KBChunk)
class KBChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index", "token_count")


@admin.register(KBScrapeSchedule)
class KBScrapeScheduleAdmin(admin.ModelAdmin):
    list_display = ("url", "org", "frequency", "is_active", "last_scraped")


@admin.register(GBPConnection)
class GBPConnectionAdmin(admin.ModelAdmin):
    list_display = ("business_name", "org", "place_id", "is_active", "last_synced")
