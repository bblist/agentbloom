from rest_framework import serializers
from .models import (
    FeatureFlag, FeatureFlagHistory, AdminAuditLog, SupportTicket,
    SupportMessage, ContentModerationQueue, SystemHealthCheck,
    ImpersonationSession, UserLifecycleEvent, RevenueAnalytics,
    PlatformMetrics,
)


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = "__all__"
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class FeatureFlagHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlagHistory
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class AdminAuditLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.CharField(source="admin_user.email", read_only=True, default="")

    class Meta:
        model = AdminAuditLog
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source="sender.email", read_only=True, default="")

    class Meta:
        model = SupportMessage
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class SupportTicketListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    org_name = serializers.CharField(source="org.name", read_only=True)
    message_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = SupportTicket
        fields = [
            "id", "subject", "status", "priority", "category",
            "user_email", "org_name", "message_count",
            "created_at", "updated_at",
        ]


class SupportTicketDetailSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = "__all__"
        read_only_fields = ("id", "org", "user", "resolved_at", "created_at", "updated_at")


class ContentModerationQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentModerationQueue
        fields = "__all__"
        read_only_fields = ("id", "reviewed_at", "created_at")


class SystemHealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealthCheck
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class ImpersonationSessionSerializer(serializers.ModelSerializer):
    admin_email = serializers.CharField(source="admin_user.email", read_only=True)
    target_email = serializers.CharField(source="target_user.email", read_only=True)

    class Meta:
        model = ImpersonationSession
        fields = "__all__"
        read_only_fields = ("id", "started_at")


class UserLifecycleEventSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserLifecycleEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class RevenueAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueAnalytics
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class PlatformMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformMetrics
        fields = "__all__"
        read_only_fields = ("id", "created_at")
