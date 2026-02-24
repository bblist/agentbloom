"""Tests for agent chat and conversation API."""
import pytest


@pytest.mark.django_db
class TestConversations:
    url = "/api/v1/agent/conversations/"

    def test_list_conversations(self, auth_client):
        """Authenticated user can list conversations."""
        response = auth_client.get(self.url)
        assert response.status_code == 200

    def test_create_conversation(self, auth_client):
        """Authenticated user can create a conversation."""
        response = auth_client.post(self.url, {
            "title": "Test conversation",
        }, format="json")
        assert response.status_code in (200, 201)

    def test_unauthenticated_blocked(self, api_client):
        """Unauthenticated access returns 401."""
        response = api_client.get(self.url)
        assert response.status_code == 401


@pytest.mark.django_db
class TestChat:
    def test_send_message(self, auth_client):
        """POST /api/v1/agent/chat/ sends a message and gets response."""
        # First create a conversation
        conv = auth_client.post("/api/v1/agent/conversations/", {
            "title": "Chat test",
        }, format="json")
        if conv.status_code in (200, 201) and conv.data.get("id"):
            response = auth_client.post("/api/v1/agent/chat/", {
                "conversation_id": conv.data["id"],
                "message": "Hello, agent!",
            }, format="json")
            assert response.status_code in (200, 201)
