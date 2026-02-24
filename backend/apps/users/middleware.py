import threading

from django.utils.deprecation import MiddlewareMixin
from .models import Organization, OrgMember

# Thread-local storage for current org
_thread_locals = threading.local()


def get_current_org():
    """Get the current organization from thread-local storage."""
    return getattr(_thread_locals, "org", None)


def _resolve_org(request):
    """
    Resolve org from X-Org-Id header. If no header is provided but the user
    belongs to exactly one org, auto-select that one.
    Sets request.org, request.org_role, and thread-local.
    """
    org_id = request.headers.get("X-Org-Id")

    if org_id:
        try:
            org = Organization.objects.get(id=org_id)
        except (Organization.DoesNotExist, ValueError):
            return
        membership = OrgMember.objects.filter(org=org, user=request.user).first()
        if membership:
            request.org = org
            request.org_role = membership.role
            _thread_locals.org = org
    else:
        # Auto-select if the user has exactly one org
        memberships = list(OrgMember.objects.filter(user=request.user).select_related("org")[:2])
        if len(memberships) == 1:
            request.org = memberships[0].org
            request.org_role = memberships[0].role
            _thread_locals.org = memberships[0].org


class OrganizationMiddleware(MiddlewareMixin):
    """
    Extract org from X-Org-Id header and attach to request.
    Validates user has membership in the org.
    Also attaches request.org_role for downstream permission checks.

    NOTE: For DRF token-authenticated requests, the user is not yet
    authenticated at middleware time.  The OrgFromHeaderMixin (below)
    resolves org lazily inside the DRF view lifecycle.
    """

    def process_request(self, request):
        request.org = None
        request.org_role = None
        _thread_locals.org = None

        if not hasattr(request, "user") or request.user.is_anonymous:
            return

        _resolve_org(request)


class OrgFromHeaderMixin:
    """
    DRF ViewSet mixin – call in ``initial()`` so that ``request.org``
    is set even when authentication happened via DRF token auth
    (which runs after Django middleware).

    Usage::

        class MyViewSet(OrgFromHeaderMixin, viewsets.ModelViewSet):
            ...
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        # If middleware already resolved the org, nothing to do.
        if getattr(request, "org", None) is not None:
            return
        # Ensure defaults exist on the request
        if not hasattr(request, "org"):
            request.org = None
        if not hasattr(request, "org_role"):
            request.org_role = None
        if request.user and request.user.is_authenticated:
            _resolve_org(request)

