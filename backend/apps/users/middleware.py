import threading

from django.utils.deprecation import MiddlewareMixin
from .models import Organization, OrgMember

# Thread-local storage for current org
_thread_locals = threading.local()


def get_current_org():
    """Get the current organization from thread-local storage."""
    return getattr(_thread_locals, "org", None)


class OrganizationMiddleware(MiddlewareMixin):
    """
    Extract org from X-Org-Id header and attach to request.
    Validates user has membership in the org.
    Also attaches request.org_role for downstream permission checks.
    """

    def process_request(self, request):
        request.org = None
        request.org_role = None
        _thread_locals.org = None

        org_id = request.headers.get("X-Org-Id")
        if not org_id or not hasattr(request, "user") or not request.user.is_authenticated:
            return

        try:
            org = Organization.objects.get(id=org_id)
        except (Organization.DoesNotExist, ValueError):
            return

        # Verify membership and capture role
        membership = OrgMember.objects.filter(org=org, user=request.user).first()
        if membership:
            request.org = org
            request.org_role = membership.role
            _thread_locals.org = org
