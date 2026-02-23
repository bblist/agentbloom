from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"orgs", views.OrganizationViewSet, basename="organization")

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("me/", views.MeView.as_view(), name="me"),
    path("onboarding/", views.OnboardingView.as_view(), name="onboarding"),
    path("", include(router.urls)),
]
