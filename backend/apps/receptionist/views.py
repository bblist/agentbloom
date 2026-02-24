"""
AI Receptionist Views

- ReceptionistConfigView: manage receptionist settings (authenticated)
- ChatSessionViewSet: view/manage chat sessions (authenticated)
- ChatAnalyticsViewSet: view analytics (authenticated)
- WidgetConfigView: public endpoint for widget to fetch config
- WidgetChatView: public endpoint for widget to send/receive messages
"""

import logging
import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReceptionistConfig, ChatSession, ChatMessage, ChatAnalytics
from .serializers import (
    ReceptionistConfigSerializer,
    ChatSessionSerializer,
    ChatSessionListSerializer,
    ChatAnalyticsSerializer,
    WidgetConfigSerializer,
    WidgetChatSerializer,
)

logger = logging.getLogger(__name__)


class ReceptionistConfigView(generics.RetrieveUpdateAPIView):
    """Get or update the receptionist config for the current org."""

    serializer_class = ReceptionistConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        org_id = self.request.headers.get("X-Org-Id")
        config, _ = ReceptionistConfig.objects.get_or_create(org_id=org_id)
        return config


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """View chat sessions for the current org."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def get_queryset(self):
        org_id = self.request.headers.get("X-Org-Id")
        qs = ChatSession.objects.filter(org_id=org_id)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        session = self.get_object()
        session.status = "closed"
        session.closed_at = timezone.now()
        session.save()
        return Response({"status": "closed"})

    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None):
        session = self.get_object()
        session.status = "transferred"
        session.save()
        # Create a system message
        ChatMessage.objects.create(
            session=session,
            role="system",
            content="Chat transferred to a human agent.",
        )
        return Response({"status": "transferred"})


class ChatAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """View chat analytics for the current org."""

    serializer_class = ChatAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Org-Id")
        return ChatAnalytics.objects.filter(org_id=org_id)


# ─── Public Widget Endpoints (no auth required) ─────────────────


class WidgetConfigView(APIView):
    """Public endpoint: widget fetches its config by embed_key."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        embed_key = request.query_params.get("key", "")
        try:
            config = ReceptionistConfig.objects.get(embed_key=embed_key)
        except ReceptionistConfig.DoesNotExist:
            return Response({"error": "Invalid widget key"}, status=404)

        if not config.is_active:
            return Response({"error": "Widget is disabled"}, status=404)

        serializer = WidgetConfigSerializer(config)
        return Response(serializer.data)


class WidgetChatView(APIView):
    """Public endpoint: widget sends a message and gets an AI response."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = WidgetChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        embed_key = request.query_params.get("key", "")
        try:
            config = ReceptionistConfig.objects.select_related("org").get(embed_key=embed_key)
        except ReceptionistConfig.DoesNotExist:
            return Response({"error": "Invalid widget key"}, status=404)

        if not config.is_active:
            return Response({"error": "Widget is disabled"}, status=404)

        # Get or create session
        session_id = data.get("session_id")
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, org=config.org)
            except ChatSession.DoesNotExist:
                session = None
        else:
            session = None

        if not session:
            session = ChatSession.objects.create(
                org=config.org,
                visitor_id=data.get("visitor_id", ""),
                visitor_name=data.get("visitor_name", ""),
                visitor_email=data.get("visitor_email", ""),
                source_url=data.get("source_url", ""),
                channel="web",
            )

        # Save visitor message
        user_msg = data["message"]
        ChatMessage.objects.create(session=session, role="visitor", content=user_msg)

        # Check for escalation keywords
        escalation_words = config.escalation_keywords or []
        should_escalate = any(
            kw.lower() in user_msg.lower() for kw in escalation_words
        )

        if should_escalate:
            escalation_response = (
                "I understand this is urgent. Let me connect you with a team member. "
                "Someone will be in touch shortly."
            )
            ChatMessage.objects.create(
                session=session, role="assistant", content=escalation_response
            )
            session.status = "transferred"
            session.save()
            return Response({
                "session_id": str(session.id),
                "response": escalation_response,
                "transferred": True,
            })

        # Check turn limit
        turn_count = session.messages.filter(role="visitor").count()
        if turn_count > config.max_ai_turns:
            limit_response = (
                "I'd love to help more, but let me connect you with a real person "
                "who can assist you further."
            )
            ChatMessage.objects.create(
                session=session, role="assistant", content=limit_response
            )
            session.status = "transferred"
            session.save()
            return Response({
                "session_id": str(session.id),
                "response": limit_response,
                "transferred": True,
            })

        # Generate AI response
        try:
            ai_response = self._generate_response(config, session, user_msg)
        except Exception as e:
            logger.error(f"Receptionist AI error: {e}")
            ai_response = (
                "I'm sorry, I'm having trouble right now. "
                "Please try again in a moment or contact us directly."
            )

        ChatMessage.objects.create(session=session, role="assistant", content=ai_response)

        # Update visitor info if provided
        if data.get("visitor_name") and not session.visitor_name:
            session.visitor_name = data["visitor_name"]
        if data.get("visitor_email") and not session.visitor_email:
            session.visitor_email = data["visitor_email"]
            session.save()

            # Create CRM contact if lead collection is enabled
            if config.can_collect_leads:
                self._create_lead(config.org, data)

        return Response({
            "session_id": str(session.id),
            "response": ai_response,
            "transferred": False,
        })

    def _generate_response(self, config, session, user_message):
        """Use OpenAI to generate a receptionist response."""
        import openai

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        # Build conversation history
        messages = [
            {
                "role": "system",
                "content": self._build_system_prompt(config),
            }
        ]

        # Add recent conversation history (last 20 messages)
        recent_msgs = session.messages.order_by("-created_at")[:20]
        for msg in reversed(list(recent_msgs)):
            role_map = {"visitor": "user", "assistant": "assistant", "system": "system"}
            messages.append({
                "role": role_map.get(msg.role, "user"),
                "content": msg.content,
            })

        # Add the current user message (not yet saved to DB at this point
        # but we already added it above, so it's in recent_msgs)

        # Fetch relevant KB context
        kb_context = self._get_kb_context(config.org, user_message)
        if kb_context:
            messages.insert(1, {
                "role": "system",
                "content": f"Relevant knowledge base information:\n{kb_context}",
            })

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def _build_system_prompt(self, config):
        """Build the system prompt for the receptionist."""
        prompt = f"""You are {config.persona_name}, a friendly and helpful AI receptionist.

Your role:
- Answer questions about the business using the knowledge base
- Be helpful, professional, and concise
- Keep responses brief (2-3 sentences unless more detail is needed)
"""
        if config.can_book_appointments:
            prompt += "- You can help visitors book appointments. Ask for their preferred date/time and contact info.\n"
        if config.can_collect_leads:
            prompt += "- Collect visitor contact information (name, email) naturally during conversation.\n"

        if config.custom_instructions:
            prompt += f"\nAdditional instructions:\n{config.custom_instructions}\n"

        prompt += "\nIf you cannot answer a question, suggest the visitor contact the business directly."

        return prompt

    def _get_kb_context(self, org, query):
        """Search the knowledge base for relevant context."""
        try:
            from apps.kb.models import KBChunk
            chunks = KBChunk.objects.filter(
                document__org=org
            ).order_by("?")[:5]  # Simple fallback; ideally use vector search
            if chunks:
                return "\n---\n".join(c.content[:500] for c in chunks)
        except Exception:
            pass
        return ""

    def _create_lead(self, org, data):
        """Create a CRM contact from visitor info."""
        try:
            from apps.email_crm.models import Contact
            Contact.objects.get_or_create(
                org=org,
                email=data["visitor_email"],
                defaults={
                    "first_name": data.get("visitor_name", "").split()[0] if data.get("visitor_name") else "",
                    "last_name": " ".join(data.get("visitor_name", "").split()[1:]) if data.get("visitor_name") else "",
                    "source": "chat_widget",
                },
            )
        except Exception as e:
            logger.warning(f"Failed to create CRM lead: {e}")
