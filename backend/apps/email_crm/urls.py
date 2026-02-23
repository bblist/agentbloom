from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"contacts", views.ContactViewSet, basename="contact")
router.register(r"segments", views.SegmentViewSet, basename="segment")
router.register(r"email-templates", views.EmailTemplateViewSet, basename="email-template")
router.register(r"campaigns", views.CampaignViewSet, basename="campaign")
router.register(r"automations", views.AutomationViewSet, basename="automation")
router.register(r"deals", views.DealViewSet, basename="deal")
router.register(r"scoring-rules", views.ScoringRuleViewSet, basename="scoring-rule")

urlpatterns = [
    path("", include(router.urls)),
]
