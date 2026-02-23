import json
import logging
import asyncio

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse

from .models import AgentConfig, Conversation, Message, ScheduledTask, AgentLearning
from .serializers import (
    AgentConfigSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    ScheduledTaskSerializer,
    ChatInputSerializer,
)
from .engine import run_agent, run_agent_streaming, AgentContext

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
    Supports both synchronous JSON response and SSE streaming (Accept: text/event-stream).
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

        # Build agent context
        config, _ = AgentConfig.objects.get_or_create(org=request.org)
        config_dict = AgentConfigSerializer(config).data

        # Load learnings for this org
        learnings = list(
            AgentLearning.objects.filter(
                org=request.org, is_active=True
            ).values("category", "corrected_output")[:10]
        )

        # Load knowledge context (last summary or recent KB entries)
        knowledge_context = conversation.summary or ""

        context = AgentContext(
            org_id=str(request.org.id),
            user_id=str(request.user.id),
            conversation_id=str(conversation.id),
            agent_config=config_dict,
            knowledge_context=knowledge_context,
            learnings=learnings,
            debug=config.debug_mode,
        )

        # Build conversation history
        conv_messages = list(
            Message.objects.filter(conversation=conversation)
            .exclude(id=user_msg.id)
            .order_by("created_at")
            .values("role", "content", "is_undone", "tool_name", "tool_result")
        )

        # Check if client wants streaming
        if request.META.get("HTTP_ACCEPT") == "text/event-stream":
            return self._stream_response(
                message_text, conv_messages, context, conversation, request.org
            )

        # Synchronous response via ReAct loop
        try:
            loop = asyncio.new_event_loop()
            agent_result = loop.run_until_complete(
                run_agent(
                    user_message=message_text,
                    conversation_messages=conv_messages,
                    context=context,
                    org=request.org,
                )
            )
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            agent_result = type("AgentResult", (), {
                "content": "I encountered an error processing your request. Please try again.",
                "model_used": "error",
                "total_tokens": 0,
                "latency_ms": 0,
                "tool_calls_made": [],
                "confidence": 0,
                "reasoning_steps": [],
            })()
        finally:
            loop.close()

        # Save assistant message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=agent_result.content,
            model_used=agent_result.model_used,
            token_count=agent_result.total_tokens,
            latency_ms=agent_result.latency_ms,
            confidence_score=agent_result.confidence,
        )

        # Save tool call messages
        for tc in agent_result.tool_calls_made:
            Message.objects.create(
                conversation=conversation,
                role="tool",
                content=json.dumps(tc.get("result", {})),
                tool_name=tc["name"],
                tool_args=tc.get("arguments", {}),
                tool_result=tc.get("result", {}),
            )

        # Update conversation token count
        conversation.total_tokens += agent_result.total_tokens
        conversation.save(update_fields=["total_tokens", "updated_at"])

        # Update org token budget
        config.tokens_used_today += agent_result.total_tokens
        config.tokens_used_month += agent_result.total_tokens
        config.save(update_fields=["tokens_used_today", "tokens_used_month"])

        return Response({
            "conversation_id": str(conversation.id),
            "user_message": MessageSerializer(user_msg).data,
            "assistant_message": MessageSerializer(assistant_msg).data,
            "tool_calls": [
                {"name": tc["name"], "result": tc.get("result", {})}
                for tc in agent_result.tool_calls_made
            ],
            "debug": {
                "model": agent_result.model_used,
                "tokens": agent_result.total_tokens,
                "latency_ms": agent_result.latency_ms,
                "steps": agent_result.reasoning_steps,
            } if context.debug else None,
        })

    def _stream_response(self, message_text, conv_messages, context, conversation, org):
        """Return a Server-Sent Events streaming response."""

        def event_stream():
            loop = asyncio.new_event_loop()
            try:
                async def _gen():
                    async for event in run_agent_streaming(
                        user_message=message_text,
                        conversation_messages=conv_messages,
                        context=context,
                        org=org,
                    ):
                        yield event

                ait = _gen().__aiter__()
                while True:
                    try:
                        event = loop.run_until_complete(ait.__anext__())
                        yield f"data: {json.dumps(event)}\n\n"
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()
            yield "data: [DONE]\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


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
