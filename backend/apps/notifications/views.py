from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification, NotificationPreference, ActivityFeedEntry
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    ActivityFeedEntrySerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, channel="in_app")

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"status": "ok"})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_read()
        return Response({"status": "ok"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})


class NotificationPreferenceSingletonView(APIView):
    """
    GET / PATCH singleton notification preferences for the current user.
    Creates a default preference object if none exists.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pref, _ = NotificationPreference.objects.get_or_create(
            user=self.request.user,
            defaults={
                "email_enabled": True,
                "push_enabled": True,
                "marketing_enabled": False,
                "digest_frequency": "daily",
            },
        )
        return pref

    def get(self, request):
        pref = self.get_object()
        return Response(NotificationPreferenceSerializer(pref).data)

    def patch(self, request):
        pref = self.get_object()
        serializer = NotificationPreferenceSerializer(pref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityFeedViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityFeedEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Org-Id")
        return ActivityFeedEntry.objects.filter(org_id=org_id)
