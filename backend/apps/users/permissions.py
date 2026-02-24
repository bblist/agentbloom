"""
RBAC permission classes for org-scoped resources.

Usage:
    from apps.users.permissions import IsOrgAdmin, IsOrgMember, IsOrgOwner

    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, IsOrgMember]
        # or
        permission_classes = [IsAuthenticated, IsOrgAdmin]  # admin + owner
"""

from rest_framework.permissions import BasePermission


class IsOrgMember(BasePermission):
    """Allow any authenticated user who is a member of the current org."""

    message = "You must be a member of this organization."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Staff/superuser bypass
        if request.user.is_staff:
            return True
        # request.org is set by OrganizationMiddleware
        org = getattr(request, "org", None)
        if not org:
            return False
        from .models import OrgMember
        return OrgMember.objects.filter(org=org, user=request.user).exists()


class IsOrgAdmin(BasePermission):
    """Allow org owners and admins only."""

    message = "You must be an admin or owner of this organization."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        org = getattr(request, "org", None)
        if not org:
            return False
        from .models import OrgMember
        return OrgMember.objects.filter(
            org=org, user=request.user, role__in=["owner", "admin"]
        ).exists()


class IsOrgOwner(BasePermission):
    """Allow only the org owner."""

    message = "You must be the owner of this organization."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        org = getattr(request, "org", None)
        if not org:
            return False
        from .models import OrgMember
        return OrgMember.objects.filter(
            org=org, user=request.user, role="owner"
        ).exists()


class ReadOnlyForMembers(BasePermission):
    """
    Members can read; admins/owners can write.
    Safe methods (GET, HEAD, OPTIONS) → any org member.
    Unsafe methods (POST, PUT, PATCH, DELETE) → admin/owner only.
    """

    message = "Members have read-only access. Admin or owner required for changes."

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        org = getattr(request, "org", None)
        if not org:
            return False
        from .models import OrgMember
        membership = OrgMember.objects.filter(
            org=org, user=request.user
        ).first()
        if not membership:
            return False
        if request.method in self.SAFE_METHODS:
            return True
        return membership.role in ("owner", "admin")
