from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.http import HttpResponse

from .models import (
    Site, Page, PageVersion, Template, Component,
    MediaLibrary, Form, FormSubmission, SiteNavigation,
)
from .serializers import (
    SiteSerializer, PageSerializer, PageVersionSerializer,
    TemplateSerializer, ComponentSerializer, MediaLibrarySerializer,
    FormSerializer, FormSubmissionSerializer, SiteNavigationSerializer,
)
from .renderer import render_page_html


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
        site.is_published = True
        site.save()
        from .tasks import publish_site_to_cdn
        publish_site_to_cdn.delay(str(site.id))
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

    @action(detail=True, methods=["get"])
    def preview(self, request, site_pk=None, pk=None):
        """Render a live HTML preview of the page."""
        page = self.get_object()
        site = page.site
        html = render_page_html(
            blocks=page.content_blocks or [],
            title=page.title,
            global_styles=site.global_styles or {},
            seo_title=page.seo_title,
            seo_description=page.seo_description,
            og_image_url=page.og_image_url,
            canonical_url=page.canonical_url,
            custom_css=page.custom_css,
            custom_js=page.custom_js,
            head_code=site.head_code,
            body_start_code=site.body_start_code,
            body_end_code=site.body_end_code,
        )
        return HttpResponse(html, content_type="text/html")

    @action(detail=True, methods=["post"])
    def publish_page(self, request, site_pk=None, pk=None):
        """Publish a single page (set status to published)."""
        page = self.get_object()
        page.status = "published"
        page.save(update_fields=["status", "updated_at"])
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
        # TODO: upload to S3, generate thumbnails via async task


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
        instance = serializer.save(
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        from .tasks import process_form_submission
        process_form_submission.delay(str(instance.id))
        return Response({"status": "submitted"}, status=status.HTTP_201_CREATED)
