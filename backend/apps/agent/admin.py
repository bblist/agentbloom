from django.contrib import admin
from .models import AgentConfig, Conversation, Message, ScheduledTask


@admin.register(AgentConfig)
class AgentConfigAdmin(admin.ModelAdmin):
    list_display = ("org", "display_name", "llm_provider", "llm_model", "tone")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "org", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "user__email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("role", "content_preview", "conversation", "model_used", "created_at")
    list_filter = ("role",)

    def content_preview(self, obj):
        return obj.content[:100]


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ("tool_name", "org", "status", "scheduled_for", "executed_at")
    list_filter = ("status",)
