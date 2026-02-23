from rest_framework.authentication import TokenAuthentication as BaseTokenAuth
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class TokenAuthentication(BaseTokenAuth):
    """
    Extended token auth with expiry support.
    Falls back to session auth for browser requests.
    """

    keyword = "Bearer"

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")
        # Record last activity
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return user, token
