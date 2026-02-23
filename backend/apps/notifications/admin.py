from django.contrib import admin
from .models import Notification, NotificationPreference, ActivityFeedEntry


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "channel", "title", "is_read", "created_at")
    list_filter = ("channel", "category", "is_read")
    search_fields = ("title", "body")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "in_app", "email", "push")


@admin.register(ActivityFeedEntry)
class ActivityFeedEntryAdmin(admin.ModelAdmin):
    list_display = ("org", "actor", "verb", "target_type", "created_at")
    list_filter = ("verb", "target_type")
