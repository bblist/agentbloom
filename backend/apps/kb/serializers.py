from rest_framework import serializers
from .models import (
    KBDocument, KBChunk, KBScrapeSchedule, GBPConnection,
    KBConflict, KBFaq, KBSearchLog,
)


class KBChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBChunk
        fields = ["id", "content", "chunk_index", "token_count", "metadata", "created_at"]
        read_only_fields = ("id", "created_at")


class KBDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBDocument
        fields = [
            "id", "title", "source_type", "source_url", "file_type",
            "status", "chunk_count", "processing_progress",
            "is_stale", "created_at", "updated_at",
        ]


class KBDocumentDetailSerializer(serializers.ModelSerializer):
    chunks = KBChunkSerializer(many=True, read_only=True)

    class Meta:
        model = KBDocument
        fields = "__all__"
        read_only_fields = (
            "id", "org", "chunk_count", "status",
            "processing_progress", "processing_step",
            "error_message", "created_at", "updated_at",
        )


class KBDocumentUploadSerializer(serializers.Serializer):
    """For file upload or URL scrape."""
    title = serializers.CharField(max_length=255)
    source_type = serializers.ChoiceField(choices=["upload", "url", "text"])
    source_url = serializers.URLField(required=False)
    raw_text = serializers.CharField(required=False)
    # file is handled via request.FILES


class KBScrapeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBScrapeSchedule
        fields = "__all__"
        read_only_fields = ("id", "org", "last_scraped", "next_scrape", "created_at")


class GBPConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GBPConnection
        fields = [
            "id", "place_id", "business_name", "is_active",
            "last_synced", "created_at",
        ]
        read_only_fields = ("id", "created_at")


class KBConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBConflict
        fields = "__all__"
        read_only_fields = ("id", "created_at", "resolved_at")


class KBFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBFaq
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at", "updated_at")


class KBSearchLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBSearchLog
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at")


class KBSearchInputSerializer(serializers.Serializer):
    query = serializers.CharField()
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)
