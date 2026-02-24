from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"settings", views.SEOSettingsViewSet, basename="seo-settings")
router.register(r"audits", views.SEOAuditViewSet, basename="seo-audit")
router.register(r"keywords", views.TrackedKeywordViewSet, basename="tracked-keyword")
router.register(r"google", views.GoogleConnectionViewSet, basename="google-connection")
router.register(r"link-suggestions", views.InternalLinkSuggestionViewSet, basename="link-suggestion")
router.register(r"page-speed", views.PageSpeedMetricsViewSet, basename="page-speed")

urlpatterns = [
    path("", include(router.urls)),
]
