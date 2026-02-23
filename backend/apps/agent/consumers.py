import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class AgentConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time agent chat.
    Streams token-by-token responses to the client.
    """

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"agent_{self.conversation_id}"
        self.user = self.scope.get("user")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "connected", "conversation_id": self.conversation_id})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """Handle incoming user message via WebSocket."""
        message_type = content.get("type", "message")

        if message_type == "message":
            user_message = content.get("content", "")
            if not user_message.strip():
                await self.send_json({"type": "error", "error": "Empty message"})
                return

            await self._handle_agent_message(user_message)

        elif message_type == "ping":
            await self.send_json({"type": "pong"})

    async def _handle_agent_message(self, user_message: str):
        """Run the ReAct agent loop and stream results to client."""
        from .models import AgentConfig, Conversation, Message, AgentLearning
        from .serializers import AgentConfigSerializer
        from .engine import run_agent_streaming, AgentContext

        # Load conversation
        try:
            conversation = await database_sync_to_async(
                Conversation.objects.select_related("org").get
            )(id=self.conversation_id)
        except Conversation.DoesNotExist:
            await self.send_json({"type": "error", "error": "Conversation not found"})
            return

        org = conversation.org

        # Save user message
        user_msg = await database_sync_to_async(Message.objects.create)(
            conversation=conversation,
            role="user",
            content=user_message,
        )

        # Build agent context
        config, _ = await database_sync_to_async(
            AgentConfig.objects.get_or_create
        )(org=org)

        config_dict = await database_sync_to_async(
            lambda: AgentConfigSerializer(config).data
        )()

        learnings = await database_sync_to_async(
            lambda: list(
                AgentLearning.objects.filter(
                    org=org, is_active=True
                ).values("category", "corrected_output")[:10]
            )
        )()

        context = AgentContext(
            org_id=str(org.id),
            user_id=str(self.user.id) if self.user else "",
            conversation_id=str(conversation.id),
            agent_config=config_dict,
            knowledge_context=conversation.summary or "",
            learnings=learnings,
            debug=config.debug_mode,
        )

        # Load conversation history
        conv_messages = await database_sync_to_async(
            lambda: list(
                Message.objects.filter(conversation=conversation)
                .exclude(id=user_msg.id)
                .order_by("created_at")
                .values("role", "content", "is_undone", "tool_name", "tool_result")
            )
        )()

        # Stream the agent response
        full_content = ""
        tool_calls_made = []
        total_tokens = 0
        model_used = ""

        try:
            async for event in run_agent_streaming(
                user_message=user_message,
                conversation_messages=conv_messages,
                context=context,
                org=org,
            ):
                event_type = event.get("type")

                if event_type == "token":
                    full_content += event.get("content", "")
                    await self.send_json({
                        "type": "token",
                        "content": event["content"],
                    })

                elif event_type == "tool_start":
                    tool_calls_made.append({
                        "name": event["tool"],
                        "args": event.get("args", {}),
                    })
                    await self.send_json({
                        "type": "tool_call",
                        "tool": event["tool"],
                        "status": "running",
                        "args": event.get("args", {}),
                    })

                elif event_type == "tool_result":
                    await self.send_json({
                        "type": "tool_result",
                        "tool": event["tool"],
                        "result": event.get("result", {}),
                        "status": "completed",
                    })

                elif event_type == "done":
                    total_tokens = event.get("usage", {}).get("total_tokens", 0)
                    if event.get("content"):
                        full_content = event["content"]

                elif event_type == "error":
                    await self.send_json({
                        "type": "error",
                        "error": event.get("error", "Unknown error"),
                    })

        except Exception as e:
            logger.error(f"Agent streaming error: {e}", exc_info=True)
            full_content = full_content or "I encountered an error. Please try again."
            await self.send_json({"type": "error", "error": str(e)})

        # Save assistant message
        assistant_msg = await database_sync_to_async(Message.objects.create)(
            conversation=conversation,
            role="assistant",
            content=full_content,
            model_used=model_used,
            token_count=total_tokens,
        )

        # Save tool messages
        for tc in tool_calls_made:
            await database_sync_to_async(Message.objects.create)(
                conversation=conversation,
                role="tool",
                content=json.dumps(tc.get("result", {})),
                tool_name=tc["name"],
                tool_args=tc.get("args", {}),
            )

        # Send done signal
        await self.send_json({
            "type": "done",
            "message_id": str(assistant_msg.id),
            "tokens": total_tokens,
        })

    async def agent_token(self, event):
        """Send a single token to the client (for streaming from channel layer)."""
        await self.send_json({
            "type": "token",
            "content": event["token"],
        })

    async def agent_done(self, event):
        """Signal that the agent has finished responding."""
        await self.send_json({
            "type": "done",
            "message_id": event.get("message_id"),
        })

    async def agent_tool_call(self, event):
        """Notify client that agent is calling a tool."""
        await self.send_json({
            "type": "tool_call",
            "tool": event["tool"],
            "status": event.get("status", "running"),
        })
