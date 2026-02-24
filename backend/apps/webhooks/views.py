from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import WebhookEndpoint, WebhookEvent, WebhookDeliveryLog, IncomingWebhook
from .serializers import (
    WebhookEndpointSerializer,
    WebhookEventSerializer,
    WebhookDeliveryLogSerializer,
)


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Org-Id")
        return WebhookEndpoint.objects.filter(org_id=org_id)

    def perform_create(self, serializer):
        org_id = self.request.headers.get("X-Org-Id")
        serializer.save(org_id=org_id)

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        """Send a test webhook to the endpoint."""
        endpoint = self.get_object()
        from .tasks import deliver_webhook
        test_payload = {
            "event": "test",
            "timestamp": timezone.now().isoformat(),
            "data": {"message": "Test webhook from AgentBloom"},
        }
        deliver_webhook.delay(
            str(endpoint.id),
            "test",
            test_payload,
        )
        return Response({"status": "test_queued"})


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WebhookEventSerializer
    permission_classes = [IsAuthenticated]
    queryset = WebhookEvent.objects.filter(is_active=True)


class WebhookDeliveryLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WebhookDeliveryLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Org-Id")
        return WebhookDeliveryLog.objects.filter(endpoint__org_id=org_id)


@api_view(["POST"])
def incoming_webhook(request, source):
    """Receive incoming webhooks from external services."""
    IncomingWebhook.objects.create(
        source=source,
        event_type=request.data.get("type", "unknown"),
        payload=request.data,
        headers=dict(request.headers),
        ip_address=request.META.get("REMOTE_ADDR"),
    )
    from .tasks import process_incoming_webhook
    process_incoming_webhook.delay(source, dict(request.data), dict(request.headers))
    return Response({"status": "received"})
