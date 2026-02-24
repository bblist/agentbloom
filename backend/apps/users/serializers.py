from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User, Organization, OrgMember, OnboardingProgress


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "avatar_url", "plan",
            "timezone", "language", "email_verified", "created_at",
        ]
        read_only_fields = ["id", "email", "email_verified", "created_at"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password")
        user = authenticate(request=self.context.get("request"), email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return {"user": user, "token": token.key}


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "full_name", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id", "name", "slug", "owner", "custom_domain", "subdomain",
            "niche", "description", "logo_url", "brand_colors", "settings",
            "created_at",
        ]
        read_only_fields = ["id", "owner", "created_at"]


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "niche", "description"]

    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid

        user = self.context["request"].user
        name = validated_data["name"]
        slug = slugify(name)
        # Ensure unique slug
        if Organization.objects.filter(slug=slug).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        org = Organization.objects.create(owner=user, slug=slug, **validated_data)
        OrgMember.objects.create(org=org, user=user, role="owner")
        OnboardingProgress.objects.create(user=user, org=org)
        return org


class OrgMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = OrgMember
        fields = ["id", "user", "role", "created_at"]
        read_only_fields = ["id", "created_at"]


class OnboardingProgressSerializer(serializers.ModelSerializer):
    completion_pct = serializers.ReadOnlyField()

    class Meta:
        model = OnboardingProgress
        fields = [
            "step_business_info", "step_branding", "step_template",
            "step_domain", "step_agent_intro", "step_tour",
            "completion_pct", "completed_at",
        ]
