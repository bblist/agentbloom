from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    SEOSettings, SEOAudit, TrackedKeyword, GoogleConnection,
    InternalLinkSuggestion, PageSpeedMetrics,
)
from .serializers import (
    SEOSettingsSerializer, SEOAuditSerializer, TrackedKeywordSerializer,
    GoogleConnectionSerializer, InternalLinkSuggestionSerializer,
    PageSpeedMetricsSerializer,
)


class SEOSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = SEOSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SEOSettings.objects.filter(site__org=self.request.org)

    @action(detail=True, methods=["post"])
    def generate_sitemap(self, request, pk=None):
        """Trigger sitemap regeneration for a site."""
        settings = self.get_object()
        # TODO: Generate sitemap XML and upload to S3 / serve from CDN
        from django.utils import timezone
        settings.sitemap_last_generated = timezone.now()
        settings.save(update_fields=["sitemap_last_generated"])
        return Response({"status": "sitemap_generated"})

    @action(detail=True, methods=["post"])
    def generate_robots(self, request, pk=None):
        """Generate robots.txt based on settings."""
        settings = self.get_object()
        sitemap_line = f"\nSitemap: {settings.sitemap_url}" if settings.sitemap_url else ""
        robots = f"User-agent: *\nAllow: /{sitemap_line}"
        settings.robots_txt = robots
        settings.save(update_fields=["robots_txt"])
        return Response({"robots_txt": robots})


class SEOAuditViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SEOAuditSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SEOAudit.objects.filter(site__org=self.request.org)

    @action(detail=False, methods=["post"])
    def run_audit(self, request):
        """Trigger an SEO audit for a site."""
        site_id = request.data.get("site_id")
        if not site_id:
            return Response({"error": "site_id required"}, status=400)

        # Build audit - check common SEO issues
        from apps.sites.models import Site, Page
        try:
            site = Site.objects.get(id=site_id, org=request.org)
        except Site.DoesNotExist:
            return Response({"error": "Site not found"}, status=404)

        pages = site.pages.all()
        issues = []
        page_scores = {}
        total_score = 100

        for page in pages:
            page_score = 100
            blocks = page.content_blocks or []

            # Check for missing title
            if not page.seo_title and not page.title:
                issues.append({
                    "type": "missing_title",
                    "severity": "high",
                    "page": str(page.id),
                    "description": f"Page '{page.title}' is missing an SEO title",
                    "fix": "Add a descriptive SEO title (50-60 characters)"
                })
                page_score -= 15

            # Check for missing meta description
            if not page.seo_description:
                issues.append({
                    "type": "missing_meta_description",
                    "severity": "medium",
                    "page": str(page.id),
                    "description": f"Page '{page.title}' is missing a meta description",
                    "fix": "Add a compelling meta description (150-160 characters)"
                })
                page_score -= 10

            # Check for hero / h1
            has_hero = any(b.get("type") == "hero" for b in blocks)
            if not has_hero:
                issues.append({
                    "type": "missing_h1",
                    "severity": "medium",
                    "page": str(page.id),
                    "description": f"Page '{page.title}' has no hero/heading block",
                    "fix": "Add a hero section with a clear H1 headline"
                })
                page_score -= 10

            # Check for images without alt text
            image_blocks = [b for b in blocks if b.get("type") == "image"]
            for img in image_blocks:
                if not img.get("props", {}).get("alt"):
                    issues.append({
                        "type": "missing_alt_text",
                        "severity": "low",
                        "page": str(page.id),
                        "description": f"Image on '{page.title}' missing alt text",
                        "fix": "Add descriptive alt text for accessibility and SEO"
                    })
                    page_score -= 5

            page_scores[str(page.id)] = max(0, page_score)

        avg_score = round(sum(page_scores.values()) / max(len(page_scores), 1))

        audit = SEOAudit.objects.create(
            site=site,
            score=avg_score,
            issues=issues,
            recommendations=[
                "Add unique SEO titles to all pages",
                "Write compelling meta descriptions",
                "Ensure every page has a clear H1 heading",
                "Add alt text to all images",
                "Enable schema markup for your business type",
            ],
            page_scores=page_scores,
            technical_score=avg_score,
            content_score=avg_score,
            performance_score=0,
            accessibility_score=0,
        )
        return Response(SEOAuditSerializer(audit).data, status=201)


class TrackedKeywordViewSet(viewsets.ModelViewSet):
    serializer_class = TrackedKeywordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TrackedKeyword.objects.filter(site__org=self.request.org)

    @action(detail=False, methods=["post"])
    def bulk_add(self, request):
        """Add multiple keywords at once."""
        site_id = request.data.get("site_id")
        keywords = request.data.get("keywords", [])
        if not site_id or not keywords:
            return Response({"error": "site_id and keywords[] required"}, status=400)
        created = []
        for kw in keywords[:50]:  # Limit 50 at a time
            obj, was_created = TrackedKeyword.objects.get_or_create(
                site_id=site_id, keyword=kw,
            )
            if was_created:
                created.append(kw)
        return Response({"added": created, "count": len(created)})


class GoogleConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = GoogleConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoogleConnection.objects.filter(org=self.request.org)


class InternalLinkSuggestionViewSet(viewsets.ModelViewSet):
    serializer_class = InternalLinkSuggestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InternalLinkSuggestion.objects.filter(site__org=self.request.org)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        suggestion = self.get_object()
        suggestion.status = "accepted"
        suggestion.save(update_fields=["status"])
        return Response({"status": "accepted"})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        suggestion = self.get_object()
        suggestion.status = "rejected"
        suggestion.save(update_fields=["status"])
        return Response({"status": "rejected"})


class PageSpeedMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PageSpeedMetricsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PageSpeedMetrics.objects.filter(page__site__org=self.request.org)
