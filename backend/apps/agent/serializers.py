from rest_framework import serializers
from .models import AgentConfig, Conversation, Message, ScheduledTask


class AgentConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentConfig
        fields = "__all__"
        read_only_fields = ["id", "org", "created_at", "updated_at"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "title", "is_active", "metadata",
            "last_message", "message_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        return MessageSerializer(msg).data if msg else None

    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ["messages"]


class ScheduledTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledTask
        fields = "__all__"
        read_only_fields = ["id", "org", "user", "created_at", "executed_at"]


class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=10000)
    conversation_id = serializers.UUIDField(required=False, allow_null=True)
