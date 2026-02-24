from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import (
    Contact, Segment, EmailTemplate, Campaign,
    Automation, Deal, ScoringRule,
)
from .serializers import (
    ContactSerializer, SegmentSerializer, EmailTemplateSerializer,
    CampaignSerializer, AutomationSerializer, DealSerializer,
    ScoringRuleSerializer,
)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def import_csv(self, request):
        """Import contacts from a CSV file."""
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response({"error": "No file provided"}, status=400)
        if not csv_file.name.endswith(".csv"):
            return Response({"error": "File must be a CSV"}, status=400)
        content = csv_file.read().decode("utf-8")
        from .tasks import import_contacts_csv
        import_contacts_csv.delay(str(self.request.org.id), content)
        return Response({"status": "import_started"})

    @action(detail=True, methods=["post"])
    def unsubscribe(self, request, pk=None):
        from django.utils import timezone
        contact = self.get_object()
        contact.is_subscribed = False
        contact.unsubscribed_at = timezone.now()
        contact.save()
        return Response({"status": "unsubscribed"})


class SegmentViewSet(viewsets.ModelViewSet):
    serializer_class = SegmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Segment.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmailTemplate.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Campaign.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status != "draft":
            return Response({"error": "Campaign must be in draft status"}, status=400)
        campaign.status = "sending"
        campaign.save()
        from .tasks import send_campaign_emails
        send_campaign_emails.delay(str(campaign.id))
        return Response({"status": "sending"})


class AutomationViewSet(viewsets.ModelViewSet):
    serializer_class = AutomationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Automation.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        automation = self.get_object()
        automation.is_active = not automation.is_active
        automation.save()
        return Response({"is_active": automation.is_active})


class DealViewSet(viewsets.ModelViewSet):
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Deal.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class ScoringRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ScoringRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScoringRule.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)
