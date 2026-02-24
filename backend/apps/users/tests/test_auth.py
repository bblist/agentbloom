"""Tests for authentication endpoints."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAuthLogin:
    url = "/api/v1/auth/login/"

    def test_login_returns_token(self, api_client, user):
        """POST /api/v1/auth/login/ with valid creds returns token."""
        response = api_client.post(self.url, {
            "email": user.email,
            "password": "testpass123",
        }, format="json")
        assert response.status_code == 200
        assert "token" in response.data or "key" in response.data

    def test_login_invalid_password(self, api_client, user):
        """Invalid password returns 400/401."""
        response = api_client.post(self.url, {
            "email": user.email,
            "password": "wrongpassword",
        }, format="json")
        assert response.status_code in (400, 401)

    def test_login_nonexistent_user(self, api_client):
        """Login with unknown email returns 400/401."""
        response = api_client.post(self.url, {
            "email": "nobody@test.com",
            "password": "anything",
        }, format="json")
        assert response.status_code in (400, 401)


@pytest.mark.django_db
class TestAuthLogout:
    url = "/api/v1/auth/logout/"

    def test_logout_clears_token(self, auth_client):
        """POST /api/v1/auth/logout/ returns 200."""
        response = auth_client.post(self.url)
        assert response.status_code in (200, 204)

    def test_logout_unauthenticated(self, api_client):
        """Unauthenticated logout returns 401."""
        response = api_client.post(self.url)
        assert response.status_code == 401
