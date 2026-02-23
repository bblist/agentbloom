import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class AgentConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time agent chat.
    Streams token-by-token responses to the client.
    """

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"agent_{self.conversation_id}"

        # TODO: authenticate user from scope
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
            # TODO: Phase 1 — run ReAct agent loop with streaming
            await self.send_json({
                "type": "assistant_message",
                "content": "WebSocket agent streaming will be implemented in Phase 1.",
                "done": True,
            })
        elif message_type == "ping":
            await self.send_json({"type": "pong"})

    async def agent_token(self, event):
        """Send a single token to the client (for streaming)."""
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
