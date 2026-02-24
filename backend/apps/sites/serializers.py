from rest_framework import serializers
from .models import (
    Site, Page, PageVersion, Template, Component,
    MediaLibrary, Form, FormSubmission, SiteNavigation,
)


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"
        read_only_fields = ["id", "org", "created_at", "updated_at"]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"
        read_only_fields = ["id", "site", "created_at", "updated_at"]
        extra_kwargs = {
            "path": {"required": False},
        }


class PageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageVersion
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = "__all__"


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = "__all__"


class MediaLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaLibrary
        fields = "__all__"
        read_only_fields = ["id", "org", "created_by", "created_at"]


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class FormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSubmission
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SiteNavigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteNavigation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
