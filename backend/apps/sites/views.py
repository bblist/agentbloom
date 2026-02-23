from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import (
    Site, Page, PageVersion, Template, Component,
    MediaLibrary, Form, FormSubmission, SiteNavigation,
)
from .serializers import (
    SiteSerializer, PageSerializer, PageVersionSerializer,
    TemplateSerializer, ComponentSerializer, MediaLibrarySerializer,
    FormSerializer, FormSubmissionSerializer, SiteNavigationSerializer,
)


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Site.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        site = self.get_object()
        from django.utils import timezone
        site.status = "published"
        site.published_at = timezone.now()
        site.save()
        # TODO: trigger static site generation / CDN invalidation
        return Response({"status": "published"})


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Page.objects.filter(site__org=self.request.org, site_id=self.kwargs.get("site_pk"))

    @action(detail=True, methods=["get"])
    def versions(self, request, site_pk=None, pk=None):
        page = self.get_object()
        versions = PageVersion.objects.filter(page=page)
        return Response(PageVersionSerializer(versions, many=True).data)

    @action(detail=True, methods=["post"])
    def rollback(self, request, site_pk=None, pk=None):
        page = self.get_object()
        version_number = request.data.get("version")
        try:
            version = PageVersion.objects.get(page=page, version_number=version_number)
        except PageVersion.DoesNotExist:
            return Response({"error": "Version not found"}, status=404)
        page.content_blocks = version.content_blocks
        page.save()
        return Response(PageSerializer(page).data)


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Template.objects.filter(is_active=True)


class ComponentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ComponentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Component.objects.filter(is_active=True)


class MediaLibraryViewSet(viewsets.ModelViewSet):
    serializer_class = MediaLibrarySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        return MediaLibrary.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org, created_by=self.request.user)
        # TODO: upload to S3, generate thumbnails


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Form.objects.filter(site__org=self.request.org)


class FormSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FormSubmissionSerializer

    def get_queryset(self):
        return FormSubmission.objects.filter(form__site__org=self.request.org)

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Public endpoint for form submissions."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        # TODO: send notification email
        return Response({"status": "submitted"}, status=status.HTTP_201_CREATED)
