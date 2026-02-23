from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Organization, OrgMember, OnboardingProgress
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    OrganizationSerializer,
    OrganizationCreateSerializer,
    OrgMemberSerializer,
    OnboardingProgressSerializer,
)


class HealthCheckView(APIView):
    """Public health-check endpoint."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {"status": "healthy", "timestamp": timezone.now().isoformat()},
            status=status.HTTP_200_OK,
        )


class RegisterView(generics.CreateAPIView):
    """User registration."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """Get / update current user profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class OrganizationViewSet(viewsets.ModelViewSet):
    """CRUD for organizations belonging to the current user."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(
            members__user=self.request.user
        ).distinct()

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        org = self.get_object()
        members = OrgMember.objects.filter(org=org).select_related("user")
        return Response(OrgMemberSerializer(members, many=True).data)

    @action(detail=True, methods=["post"])
    def invite(self, request, pk=None):
        org = self.get_object()
        email = request.data.get("email")
        role = request.data.get("role", "member")
        if not email:
            return Response({"error": "Email is required"}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # TODO: send invite email to create account
            return Response({"status": "invite_sent"})

        OrgMember.objects.get_or_create(org=org, user=user, defaults={"role": role})
        return Response({"status": "member_added"})


class OnboardingView(generics.RetrieveUpdateAPIView):
    """Get / update onboarding progress."""

    serializer_class = OnboardingProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        org_id = self.request.headers.get("X-Org-Id")
        return OnboardingProgress.objects.get(
            user=self.request.user, org_id=org_id
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.completion_pct == 100 and not instance.completed_at:
            instance.completed_at = timezone.now()
            instance.save()
