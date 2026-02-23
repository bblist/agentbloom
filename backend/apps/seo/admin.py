from django.contrib import admin
from .models import SEOSettings, SEOAudit, TrackedKeyword, GoogleConnection


@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ("site", "auto_seo_enabled", "schema_markup_enabled", "local_seo_enabled")


@admin.register(SEOAudit)
class SEOAuditAdmin(admin.ModelAdmin):
    list_display = ("site", "score", "created_at")


@admin.register(TrackedKeyword)
class TrackedKeywordAdmin(admin.ModelAdmin):
    list_display = ("keyword", "site", "current_rank", "previous_rank", "search_volume")


@admin.register(GoogleConnection)
class GoogleConnectionAdmin(admin.ModelAdmin):
    list_display = ("org", "service", "property_url", "is_active", "last_synced")
