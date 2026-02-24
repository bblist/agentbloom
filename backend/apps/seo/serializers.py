from rest_framework import serializers
from .models import (
    SEOSettings, SEOAudit, TrackedKeyword, GoogleConnection,
    InternalLinkSuggestion, PageSpeedMetrics,
)


class SEOSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOSettings
        fields = "__all__"
        read_only_fields = (
            "id", "sitemap_url", "sitemap_last_generated",
            "google_search_console_verified", "created_at", "updated_at",
        )


class SEOAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOAudit
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class TrackedKeywordSerializer(serializers.ModelSerializer):
    rank_change = serializers.SerializerMethodField()

    class Meta:
        model = TrackedKeyword
        fields = "__all__"
        read_only_fields = (
            "id", "current_rank", "previous_rank", "best_rank",
            "search_volume", "difficulty", "last_checked", "history", "created_at",
        )

    def get_rank_change(self, obj):
        if obj.previous_rank and obj.current_rank:
            return obj.previous_rank - obj.current_rank
        return None


class GoogleConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleConnection
        fields = ["id", "service", "property_url", "is_active", "last_synced", "created_at"]
        read_only_fields = ("id", "created_at")


class InternalLinkSuggestionSerializer(serializers.ModelSerializer):
    source_page_title = serializers.CharField(source="source_page.title", read_only=True)
    target_page_title = serializers.CharField(source="target_page.title", read_only=True)

    class Meta:
        model = InternalLinkSuggestion
        fields = "__all__"
        read_only_fields = ("id", "confidence", "created_at")


class PageSpeedMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSpeedMetrics
        fields = "__all__"
        read_only_fields = ("id", "measured_at")
