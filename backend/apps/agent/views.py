import json
import logging

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AgentConfig, Conversation, Message, ScheduledTask
from .serializers import (
    AgentConfigSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    ScheduledTaskSerializer,
    ChatInputSerializer,
)

logger = logging.getLogger(__name__)


class AgentConfigView(APIView):
    """Get / update agent configuration for current org."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        config, _ = AgentConfig.objects.get_or_create(org=request.org)
        return Response(AgentConfigSerializer(config).data)

    def patch(self, request):
        config, _ = AgentConfig.objects.get_or_create(org=request.org)
        serializer = AgentConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """Manage conversation threads."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConversationDetailSerializer
        return ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            org=self.request.org, user=self.request.user
        ).prefetch_related("messages")

    def perform_create(self, serializer):
        serializer.save(org=self.request.org, user=self.request.user)


class ChatView(APIView):
    """
    Send a message to the agent and get a response.
    POST /api/v1/agent/chat/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message_text = serializer.validated_data["message"]
        conversation_id = serializer.validated_data.get("conversation_id")

        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id, org=request.org, user=request.user
                )
            except Conversation.DoesNotExist:
                return Response({"error": "Conversation not found"}, status=404)
        else:
            conversation = Conversation.objects.create(
                org=request.org,
                user=request.user,
                title=message_text[:100],
            )

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role="user",
            content=message_text,
        )

        # TODO: Phase 1 — wire up ReAct agent loop here
        # For now, return a placeholder response
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content="Thanks for your message! The AI agent is being set up and will be available soon. "
                    "In the meantime, feel free to explore the dashboard.",
            model_used="placeholder",
        )

        return Response({
            "conversation_id": str(conversation.id),
            "user_message": MessageSerializer(user_msg).data,
            "assistant_message": MessageSerializer(assistant_msg).data,
        })


class ScheduledTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """View scheduled tasks for current org."""

    serializer_class = ScheduledTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScheduledTask.objects.filter(org=self.request.org)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        task = self.get_object()
        if task.status == "pending":
            task.status = "cancelled"
            task.save()
            return Response({"status": "cancelled"})
        return Response({"error": "Can only cancel pending tasks"}, status=400)
