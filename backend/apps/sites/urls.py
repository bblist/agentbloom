from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views

router = DefaultRouter()
router.register(r"sites", views.SiteViewSet, basename="site")
router.register(r"templates", views.TemplateViewSet, basename="template")
router.register(r"components", views.ComponentViewSet, basename="component")
router.register(r"media", views.MediaLibraryViewSet, basename="media")
router.register(r"forms", views.FormViewSet, basename="form")
router.register(r"submissions", views.FormSubmissionViewSet, basename="submission")

# Nested: /sites/{site_pk}/pages/
sites_router = NestedDefaultRouter(router, r"sites", lookup="site")
sites_router.register(r"pages", views.PageViewSet, basename="site-page")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(sites_router.urls)),
]
