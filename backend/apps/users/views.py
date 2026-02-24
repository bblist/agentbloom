from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Organization, OrgMember, OnboardingProgress
from .serializers import (
    LoginSerializer,
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
        token = Token.objects.get(user=user)
        return Response(
            {"user": UserSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Email + password login → returns Bearer token."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(
            {"user": UserSerializer(result["user"]).data, "token": result["token"]},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Delete current token to log out."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.auth.delete()
        except Exception:
            pass
        return Response({"detail": "Logged out."}, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """Rotate token: delete old, issue new."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        token = Token.objects.create(user=request.user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


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
            # Queue invite email via SES
            from apps.notifications.tasks import send_notification_email
            send_notification_email.delay(
                to_email=email,
                subject=f"You've been invited to {org.name} on AgentBloom",
                body=f"Join {org.name} at https://agentbloom.nobleblocks.com/auth/register?invite={org.id}&email={email}",
            )
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
