from django.contrib import admin
from .models import ReceptionistConfig, ChatSession, ChatMessage, ChatAnalytics


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "content", "created_at")
    ordering = ("created_at",)


@admin.register(ReceptionistConfig)
class ReceptionistConfigAdmin(admin.ModelAdmin):
    list_display = ("org", "persona_name", "is_active", "language", "created_at")
    list_filter = ("is_active", "language")
    search_fields = ("org__name", "persona_name")
    readonly_fields = ("embed_key", "created_at", "updated_at")


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "org",
        "visitor_name",
        "visitor_email",
        "status",
        "channel",
        "created_at",
    )
    list_filter = ("status", "channel", "created_at")
    search_fields = ("visitor_name", "visitor_email", "visitor_id")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ChatMessageInline]


@admin.register(ChatAnalytics)
class ChatAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "org",
        "date",
        "total_sessions",
        "ai_resolved",
        "transferred",
        "leads_collected",
        "appointments_booked",
    )
    list_filter = ("date",)
    search_fields = ("org__name",)
