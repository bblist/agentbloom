"""
WebSocket consumer for real-time receptionist chat.

Widget connects via ws://.../ws/receptionist/<embed_key>/
No auth required (public widget).
"""

import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class ReceptionistConsumer(AsyncJsonWebsocketConsumer):
    """Real-time chat consumer for the AI receptionist widget."""

    async def connect(self):
        self.embed_key = self.scope["url_route"]["kwargs"]["embed_key"]
        self.session_id = None
        self.room_group_name = f"receptionist_{self.embed_key}"

        # Validate embed key
        config = await self._get_config()
        if not config or not config.is_active:
            await self.close()
            return

        self.config = config
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send greeting
        await self.send_json({
            "type": "connected",
            "greeting": config.greeting_message,
            "persona_name": config.persona_name,
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        msg_type = content.get("type", "message")

        if msg_type == "message":
            user_message = content.get("content", "")
            visitor_id = content.get("visitor_id", "")
            visitor_name = content.get("visitor_name", "")
            visitor_email = content.get("visitor_email", "")
            source_url = content.get("source_url", "")

            if not user_message.strip():
                await self.send_json({"type": "error", "error": "Empty message"})
                return

            await self.send_json({"type": "thinking"})

            session = await self._get_or_create_session(
                visitor_id, visitor_name, visitor_email, source_url
            )
            self.session_id = str(session.id)

            # Save user message
            await self._save_message(session, "visitor", user_message)

            # Check escalation
            should_escalate = await self._check_escalation(user_message)
            if should_escalate:
                response = (
                    "I understand this is important. Let me connect you with a team member. "
                    "Someone will be in touch shortly."
                )
                await self._save_message(session, "assistant", response)
                await self._update_session_status(session, "transferred")
                await self.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": response,
                    "session_id": self.session_id,
                    "transferred": True,
                })
                return

            # Generate AI response
            try:
                response = await self._generate_response(session, user_message)
            except Exception as e:
                logger.error(f"Receptionist WS AI error: {e}")
                response = (
                    "I'm sorry, I'm having trouble right now. "
                    "Please try again in a moment."
                )

            await self._save_message(session, "assistant", response)
            await self.send_json({
                "type": "message",
                "role": "assistant",
                "content": response,
                "session_id": self.session_id,
            })

        elif msg_type == "ping":
            await self.send_json({"type": "pong"})

    # ─── Database helpers ──────────────────────────

    @database_sync_to_async
    def _get_config(self):
        from .models import ReceptionistConfig
        try:
            return ReceptionistConfig.objects.select_related("org").get(
                embed_key=self.embed_key
            )
        except ReceptionistConfig.DoesNotExist:
            return None

    @database_sync_to_async
    def _get_or_create_session(self, visitor_id, visitor_name, visitor_email, source_url):
        from .models import ChatSession

        # Try to reuse an active session for same visitor
        if self.session_id:
            try:
                return ChatSession.objects.get(id=self.session_id)
            except ChatSession.DoesNotExist:
                pass

        if visitor_id:
            existing = (
                ChatSession.objects.filter(
                    org=self.config.org,
                    visitor_id=visitor_id,
                    status="active",
                )
                .order_by("-created_at")
                .first()
            )
            if existing:
                return existing

        return ChatSession.objects.create(
            org=self.config.org,
            visitor_id=visitor_id or "",
            visitor_name=visitor_name or "",
            visitor_email=visitor_email or "",
            source_url=source_url or "",
            channel="web",
        )

    @database_sync_to_async
    def _save_message(self, session, role, content):
        from .models import ChatMessage
        return ChatMessage.objects.create(session=session, role=role, content=content)

    @database_sync_to_async
    def _update_session_status(self, session, status):
        session.status = status
        session.save()

    @database_sync_to_async
    def _check_escalation(self, message):
        keywords = self.config.escalation_keywords or []
        return any(kw.lower() in message.lower() for kw in keywords)

    @database_sync_to_async
    def _generate_response(self, session, user_message):
        """Synchronous AI call wrapped for async."""
        import openai
        from django.conf import settings
        from .models import ChatMessage

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        system_prompt = self._build_prompt_sync()

        messages = [{"role": "system", "content": system_prompt}]

        # Add KB context
        kb_context = self._get_kb_sync()
        if kb_context:
            messages.append({"role": "system", "content": f"Knowledge base:\n{kb_context}"})

        # Recent history
        recent = list(
            ChatMessage.objects.filter(session=session).order_by("-created_at")[:20]
        )
        for msg in reversed(recent):
            role_map = {"visitor": "user", "assistant": "assistant", "system": "system"}
            messages.append({"role": role_map.get(msg.role, "user"), "content": msg.content})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def _build_prompt_sync(self):
        config = self.config
        prompt = f"""You are {config.persona_name}, a friendly and helpful AI receptionist.
Keep responses brief (2-3 sentences unless more detail is needed).
Be professional, warm, and helpful."""
        if config.can_book_appointments:
            prompt += "\nYou can help visitors book appointments."
        if config.can_collect_leads:
            prompt += "\nCollect visitor contact information naturally."
        if config.custom_instructions:
            prompt += f"\n{config.custom_instructions}"
        return prompt

    def _get_kb_sync(self):
        try:
            from apps.kb.models import KBChunk
            chunks = KBChunk.objects.filter(document__org=self.config.org).order_by("?")[:5]
            if chunks:
                return "\n---\n".join(c.content[:500] for c in chunks)
        except Exception:
            pass
        return ""
