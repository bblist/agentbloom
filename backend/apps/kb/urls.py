from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"documents", views.KBDocumentViewSet, basename="kb-document")
router.register(r"chunks", views.KBChunkViewSet, basename="kb-chunk")
router.register(r"search", views.KBSearchView, basename="kb-search")
router.register(r"sources", views.KBScrapeScheduleViewSet, basename="kb-scrape")
router.register(r"gbp", views.GBPConnectionViewSet, basename="gbp")
router.register(r"conflicts", views.KBConflictViewSet, basename="kb-conflict")
router.register(r"faqs", views.KBFaqViewSet, basename="kb-faq")
router.register(r"search-logs", views.KBSearchLogViewSet, basename="kb-search-log")

urlpatterns = [
    path("", include(router.urls)),
]
