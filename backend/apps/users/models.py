import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager — email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model — email as primary identifier."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    avatar_url = models.URLField(blank=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    plan = models.CharField(
        max_length=50,
        choices=[
            ("free", "Free"),
            ("starter", "Starter"),
            ("pro", "Pro"),
            ("enterprise", "Enterprise"),
        ],
        default="free",
    )
    timezone = models.CharField(max_length=100, default="UTC")
    language = models.CharField(max_length=10, default="en")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Organization(models.Model):
    """Organization / workspace — all resources are scoped to an org."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_orgs")
    custom_domain = models.CharField(max_length=255, blank=True)
    subdomain = models.CharField(max_length=255, unique=True, blank=True, null=True)
    niche = models.CharField(max_length=100, blank=True)  # hvac, yoga, restaurant, etc.
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    brand_colors = models.JSONField(default=dict, blank=True)  # {primary, secondary, accent}
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organizations"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class OrgMember(models.Model):
    """Organization membership — links users to orgs with roles."""

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="member")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "org_members"
        unique_together = ("org", "user")

    def __str__(self):
        return f"{self.user.email} @ {self.org.name} ({self.role})"


class AuditLog(models.Model):
    """Audit trail for all mutations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.UUIDField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["org", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at}"


class OnboardingProgress(models.Model):
    """Track user onboarding completion."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="onboarding")
    org = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="onboarding")
    step_business_info = models.BooleanField(default=False)
    step_branding = models.BooleanField(default=False)
    step_template = models.BooleanField(default=False)
    step_domain = models.BooleanField(default=False)
    step_agent_intro = models.BooleanField(default=False)
    step_tour = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "onboarding_progress"

    @property
    def completion_pct(self):
        steps = [
            self.step_business_info,
            self.step_branding,
            self.step_template,
            self.step_domain,
            self.step_agent_intro,
            self.step_tour,
        ]
        return int(sum(steps) / len(steps) * 100)
