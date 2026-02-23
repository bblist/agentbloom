from django.contrib import admin
from .models import (
    FeatureFlag, AdminAuditLog, SupportTicket,
    ContentModerationQueue, SystemHealthCheck,
)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("name", "is_enabled", "rollout_percentage", "updated_at")
    list_filter = ("is_enabled",)


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "admin_user", "target_type", "created_at")
    list_filter = ("action",)
    readonly_fields = [field.name for field in AdminAuditLog._meta.fields]


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "org", "status", "priority", "assigned_to", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("subject", "user__email")


@admin.register(ContentModerationQueue)
class ContentModerationQueueAdmin(admin.ModelAdmin):
    list_display = ("content_type", "org", "reason", "status", "created_at")
    list_filter = ("status", "content_type")


@admin.register(SystemHealthCheck)
class SystemHealthCheckAdmin(admin.ModelAdmin):
    list_display = ("service", "status", "response_time_ms", "created_at")
    list_filter = ("service", "status")
