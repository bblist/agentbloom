from rest_framework import serializers
from .models import (
    Contact, Segment, EmailTemplate, Campaign, CampaignEvent,
    Automation, AutomationEnrollment, Deal, ScoringRule,
)


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Contact
        fields = "__all__"
        read_only_fields = ["id", "org", "lead_score", "created_at", "updated_at"]


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = "__all__"
        read_only_fields = ["id", "org", "contact_count", "created_at", "updated_at"]


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = "__all__"
        read_only_fields = ["id", "org", "created_at", "updated_at"]


class CampaignSerializer(serializers.ModelSerializer):
    open_rate = serializers.ReadOnlyField()
    click_rate = serializers.ReadOnlyField()

    class Meta:
        model = Campaign
        fields = "__all__"
        read_only_fields = [
            "id", "org", "total_sent", "total_delivered", "total_opens",
            "total_clicks", "total_bounces", "total_complaints",
            "total_unsubscribes", "sent_at", "created_at", "updated_at",
        ]


class CampaignEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignEvent
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = "__all__"
        read_only_fields = ["id", "org", "enrolled_count", "created_at", "updated_at"]


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = "__all__"
        read_only_fields = ["id", "org", "created_at", "updated_at"]


class ScoringRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringRule
        fields = "__all__"
        read_only_fields = ["id", "org", "created_at"]
