from rest_framework import serializers
from .models import Notification, NotificationPreference, ActivityFeedEntry


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at")


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ("id", "user")


class ActivityFeedEntrySerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.full_name", read_only=True, default="")

    class Meta:
        model = ActivityFeedEntry
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at")
