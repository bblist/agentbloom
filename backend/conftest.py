"""Shared test fixtures and factories for AgentBloom."""
import pytest
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


# -----------------------------------------------------------------------
# Factories
# -----------------------------------------------------------------------

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    full_name = factory.Faker("name")
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "testpass123")
        if create:
            self.save()


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = "users.Organization"

    name = factory.Sequence(lambda n: f"Test Org {n}")
    slug = factory.Sequence(lambda n: f"test-org-{n}")
    owner = factory.SubFactory(UserFactory)


class OrgMemberFactory(DjangoModelFactory):
    class Meta:
        model = "users.OrgMember"

    org = factory.SubFactory(OrganizationFactory)
    user = factory.SubFactory(UserFactory)
    role = "member"


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------

@pytest.fixture
def user(db):
    """Create a basic test user."""
    return UserFactory()


@pytest.fixture
def admin_user(db):
    """Create a staff/admin user."""
    return UserFactory(is_staff=True, is_admin=True)


@pytest.fixture
def org(db, user):
    """Create a test org owned by the default user."""
    org = OrganizationFactory(owner=user)
    OrgMemberFactory(org=org, user=user, role="owner")
    return org


@pytest.fixture
def member_user(db, org):
    """Create a user who is a member (not admin) of the test org."""
    u = UserFactory()
    OrgMemberFactory(org=org, user=u, role="member")
    return u


@pytest.fixture
def api_client():
    """DRF API client instance."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(api_client, user, org):
    """Authenticated API client with org header."""
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token.key}",
        HTTP_X_ORG_ID=str(org.id),
    )
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Authenticated API client for staff user."""
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    return api_client
