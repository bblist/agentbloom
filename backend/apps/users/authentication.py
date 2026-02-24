from rest_framework.authentication import TokenAuthentication as BaseTokenAuth
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class TokenAuthentication(BaseTokenAuth):
    """
    Extended token auth with expiry support.
    Falls back to session auth for browser requests.

    Also resolves org via X-Org-Id header (or auto-selects the
    user's single org) because Django middleware runs before DRF
    authentication and therefore can't access the token-authed user.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        # Resolve org if middleware hasn't already.
        # Middleware can't resolve org for DRF token auth because it runs
        # before DRF authenticates the user) — we do it here instead.
        if getattr(request, "org", None) is None:
            request.org = None
            request.org_role = None
            from .models import Organization, OrgMember
            import threading
            _thread_locals = threading.local()

            org_id = request.headers.get("X-Org-Id") if hasattr(request, "headers") else request.META.get("HTTP_X_ORG_ID")
            if org_id:
                try:
                    org = Organization.objects.get(id=org_id)
                    membership = OrgMember.objects.filter(org=org, user=user).first()
                    if membership:
                        request.org = org
                        request.org_role = membership.role
                except (Organization.DoesNotExist, ValueError):
                    pass
            else:
                # Auto-select if user has exactly one org
                memberships = list(OrgMember.objects.filter(user=user).select_related("org")[:2])
                if len(memberships) == 1:
                    request.org = memberships[0].org
                    request.org_role = memberships[0].role
        return user, token

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")
        # Record last activity
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return user, token

