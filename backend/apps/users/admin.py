from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, OrgMember, AuditLog, OnboardingProgress


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "plan", "is_active", "is_staff", "created_at")
    list_filter = ("plan", "is_active", "is_staff", "created_at")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "avatar_url", "plan", "timezone", "language")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_admin", "is_superuser", "groups", "user_permissions")}),
        ("Metadata", {"fields": ("email_verified", "metadata")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "niche", "created_at")
    list_filter = ("niche", "created_at")
    search_fields = ("name", "slug", "owner__email")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OrgMember)
class OrgMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "org", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__email", "org__name")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "org", "resource_type", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("action", "user__email", "resource_type")
    readonly_fields = ("id", "user", "org", "action", "resource_type", "resource_id", "details", "ip_address", "created_at")


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "org", "completion_pct", "completed_at")
    readonly_fields = ("completion_pct",)
