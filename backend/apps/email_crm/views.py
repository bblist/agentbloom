from rest_framework import permissions, viewsets
from rest_framework.decorators import action
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

    @action(detail=False, methods=["post"])
    def import_csv(self, request):
        # TODO: Parse CSV and create contacts
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
        campaign.status = "scheduled"
        campaign.save()
        # TODO: Celery task to send emails via SES
        return Response({"status": "sending_scheduled"})


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
