from django.contrib import admin
from .models import Contact, Segment, EmailTemplate, Campaign, Automation, Deal, ScoringRule


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "org", "source", "lead_score", "is_subscribed")
    list_filter = ("source", "is_subscribed")
    search_fields = ("email", "first_name", "last_name")


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "is_dynamic", "contact_count")


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "subject", "is_active")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "status", "total_sent", "total_opens", "total_clicks")
    list_filter = ("status",)


@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "trigger_type", "is_active", "enrolled_count")
    list_filter = ("is_active",)


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("title", "contact", "value", "stage", "probability")
    list_filter = ("stage",)


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "points", "is_active")
