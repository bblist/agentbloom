"""Tests for RBAC permission classes."""
import pytest
from rest_framework.test import APIRequestFactory
from apps.users.permissions import IsOrgMember, IsOrgAdmin, IsOrgOwner, ReadOnlyForMembers
from conftest import UserFactory, OrganizationFactory, OrgMemberFactory


factory = APIRequestFactory()


@pytest.mark.django_db
class TestIsOrgMember:
    def test_member_allowed(self, user, org):
        request = factory.get("/fake/")
        request.user = user
        request.org = org
        assert IsOrgMember().has_permission(request, None) is True

    def test_non_member_denied(self, db):
        outsider = UserFactory()
        org = OrganizationFactory()
        request = factory.get("/fake/")
        request.user = outsider
        request.org = org
        assert IsOrgMember().has_permission(request, None) is False

    def test_staff_always_allowed(self, admin_user, org):
        request = factory.get("/fake/")
        request.user = admin_user
        request.org = org
        assert IsOrgMember().has_permission(request, None) is True


@pytest.mark.django_db
class TestIsOrgAdmin:
    def test_admin_allowed(self, db):
        org = OrganizationFactory()
        admin = UserFactory()
        OrgMemberFactory(org=org, user=admin, role="admin")
        request = factory.get("/fake/")
        request.user = admin
        request.org = org
        assert IsOrgAdmin().has_permission(request, None) is True

    def test_member_denied(self, member_user, org):
        request = factory.get("/fake/")
        request.user = member_user
        request.org = org
        assert IsOrgAdmin().has_permission(request, None) is False

    def test_owner_allowed(self, user, org):
        request = factory.get("/fake/")
        request.user = user
        request.org = org
        assert IsOrgAdmin().has_permission(request, None) is True


@pytest.mark.django_db
class TestReadOnlyForMembers:
    def test_member_can_read(self, member_user, org):
        request = factory.get("/fake/")
        request.user = member_user
        request.org = org
        assert ReadOnlyForMembers().has_permission(request, None) is True

    def test_member_cannot_write(self, member_user, org):
        request = factory.post("/fake/")
        request.user = member_user
        request.org = org
        assert ReadOnlyForMembers().has_permission(request, None) is False

    def test_admin_can_write(self, db):
        org = OrganizationFactory()
        admin = UserFactory()
        OrgMemberFactory(org=org, user=admin, role="admin")
        request = factory.post("/fake/")
        request.user = admin
        request.org = org
        assert ReadOnlyForMembers().has_permission(request, None) is True
