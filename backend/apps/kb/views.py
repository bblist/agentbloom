from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q

from .models import (
    KBDocument, KBChunk, KBScrapeSchedule, GBPConnection,
    KBConflict, KBFaq, KBSearchLog,
)
from .serializers import (
    KBDocumentListSerializer, KBDocumentDetailSerializer,
    KBDocumentUploadSerializer, KBChunkSerializer,
    KBScrapeScheduleSerializer, GBPConnectionSerializer,
    KBConflictSerializer, KBFaqSerializer, KBSearchLogSerializer,
    KBSearchInputSerializer,
)


class KBDocumentViewSet(viewsets.ModelViewSet):
    """Knowledge base document CRUD + upload + processing."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = KBDocument.objects.filter(org=self.request.org)
        source_type = self.request.query_params.get("source_type")
        if source_type:
            qs = qs.filter(source_type=source_type)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return KBDocumentListSerializer
        if self.action == "create":
            return KBDocumentUploadSerializer
        return KBDocumentDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = KBDocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        doc = KBDocument.objects.create(
            org=request.org,
            title=data["title"],
            source_type=data["source_type"],
            source_url=data.get("source_url", ""),
            raw_text=data.get("raw_text", ""),
            status="pending",
        )

        # Handle file upload
        if "file" in request.FILES:
            uploaded = request.FILES["file"]
            doc.file_type = uploaded.name.split(".")[-1].lower()
            # TODO: Upload to S3 and set doc.file_url
            doc.raw_text = uploaded.read().decode("utf-8", errors="replace")
            doc.save()

        # TODO: Trigger Celery task to process document
        # from .tasks import process_kb_document
        # process_kb_document.delay(str(doc.id))

        return Response(KBDocumentDetailSerializer(doc).data, status=201)

    def perform_create(self, serializer):
        pass  # handled in create()

    @action(detail=True, methods=["post"])
    def reprocess(self, request, pk=None):
        """Re-process document (re-chunk + re-embed)."""
        doc = self.get_object()
        doc.status = "pending"
        doc.processing_progress = 0
        doc.save(update_fields=["status", "processing_progress"])
        # TODO: Trigger Celery task
        return Response({"status": "reprocessing"})

    @action(detail=True, methods=["post"])
    def mark_verified(self, request, pk=None):
        """Mark document content as verified/current."""
        doc = self.get_object()
        from django.utils import timezone
        doc.is_stale = False
        doc.last_verified = timezone.now()
        doc.save(update_fields=["is_stale", "last_verified"])
        return Response({"status": "verified"})

    @action(detail=True, methods=["post"])
    def mark_stale(self, request, pk=None):
        """Flag document as outdated."""
        doc = self.get_object()
        doc.is_stale = True
        doc.stale_reason = request.data.get("reason", "Manually flagged")
        doc.save(update_fields=["is_stale", "stale_reason"])
        return Response({"status": "marked_stale"})


class KBChunkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = KBChunkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KBChunk.objects.filter(document__org=self.request.org)


class KBSearchView(viewsets.ViewSet):
    """Semantic search across KB documents."""
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """POST /kb/search/ — semantic search."""
        serializer = KBSearchInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data["query"]
        top_k = serializer.validated_data.get("top_k", 5)

        # Text search fallback (until embeddings are set up)
        chunks = KBChunk.objects.filter(
            document__org=request.org,
            document__status="completed",
        ).filter(
            Q(content__icontains=query)
        )[:top_k]

        # Log the search
        KBSearchLog.objects.create(
            org=request.org,
            query=query,
            results_count=chunks.count(),
            source="dashboard",
        )

        results = []
        for chunk in chunks:
            results.append({
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "document_title": chunk.document.title,
                "content": chunk.content,
                "chunk_index": chunk.chunk_index,
                "score": 1.0,  # Placeholder until vector search
            })

        return Response({"results": results, "query": query})


class KBScrapeScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = KBScrapeScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KBScrapeSchedule.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=True, methods=["post"])
    def scrape_now(self, request, pk=None):
        """Trigger immediate scrape."""
        schedule = self.get_object()
        # TODO: Trigger Celery task
        return Response({"status": "scraping", "url": schedule.url})


class GBPConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = GBPConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GBPConnection.objects.filter(org=self.request.org)


class KBConflictViewSet(viewsets.ModelViewSet):
    serializer_class = KBConflictSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KBConflict.objects.filter(org=self.request.org)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        conflict = self.get_object()
        from django.utils import timezone
        conflict.status = "resolved"
        conflict.resolution = request.data.get("resolution", "")
        conflict.resolved_by = request.user
        conflict.resolved_at = timezone.now()
        conflict.save()
        return Response(KBConflictSerializer(conflict).data)

    @action(detail=True, methods=["post"])
    def ignore(self, request, pk=None):
        conflict = self.get_object()
        conflict.status = "ignored"
        conflict.save(update_fields=["status"])
        return Response({"status": "ignored"})


class KBFaqViewSet(viewsets.ModelViewSet):
    serializer_class = KBFaqSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = KBFaq.objects.filter(org=self.request.org)
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(org=self.request.org, is_auto_generated=False)


class KBSearchLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = KBSearchLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KBSearchLog.objects.filter(org=self.request.org)[:100]
