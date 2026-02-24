from rest_framework import serializers
from .models import ReceptionistConfig, ChatSession, ChatMessage, ChatAnalytics


class ReceptionistConfigSerializer(serializers.ModelSerializer):
    embed_snippet = serializers.SerializerMethodField()

    class Meta:
        model = ReceptionistConfig
        fields = [
            "id", "is_active", "persona_name", "greeting_message", "avatar_url",
            "primary_color", "position", "business_hours", "after_hours_message",
            "language", "max_ai_turns", "escalation_keywords", "custom_instructions",
            "can_book_appointments", "can_collect_leads", "can_answer_faq",
            "embed_key", "embed_snippet", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "embed_key", "embed_snippet", "created_at", "updated_at"]

    def get_embed_snippet(self, obj):
        from django.conf import settings
        base_url = settings.FRONTEND_URL
        return (
            f'<script src="{base_url}/widget/chat.js" '
            f'data-key="{obj.embed_key}" async></script>'
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            "id", "visitor_id", "visitor_name", "visitor_email", "status",
            "channel", "sentiment_score", "actions_taken", "source_url",
            "created_at", "closed_at", "messages", "message_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view (no messages)."""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            "id", "visitor_name", "visitor_email", "status", "channel",
            "sentiment_score", "source_url", "created_at", "closed_at",
            "message_count", "last_message",
        ]

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if msg:
            return {"role": msg.role, "content": msg.content[:100], "created_at": msg.created_at}
        return None


class ChatAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAnalytics
        fields = [
            "id", "date", "total_sessions", "ai_resolved", "transferred",
            "leads_collected", "appointments_booked",
            "avg_messages_per_session", "avg_sentiment", "top_queries",
        ]


class WidgetConfigSerializer(serializers.Serializer):
    """Public-facing config returned to the chat widget (no secrets)."""
    persona_name = serializers.CharField()
    greeting_message = serializers.CharField()
    avatar_url = serializers.CharField()
    primary_color = serializers.CharField()
    position = serializers.CharField()
    is_active = serializers.BooleanField()
    can_book_appointments = serializers.BooleanField()


class WidgetChatSerializer(serializers.Serializer):
    """Incoming chat message from widget."""
    message = serializers.CharField(max_length=2000)
    session_id = serializers.UUIDField(required=False, allow_null=True)
    visitor_id = serializers.CharField(max_length=255, required=False, default="")
    visitor_name = serializers.CharField(max_length=255, required=False, default="")
    visitor_email = serializers.EmailField(required=False, default="")
    source_url = serializers.URLField(required=False, default="")
