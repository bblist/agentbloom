from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"orgs", views.OrganizationViewSet, basename="organization")

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("google/", views.GoogleAuthView.as_view(), name="google-auth"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("token/refresh/", views.TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", views.MeView.as_view(), name="me"),
    path("me/data-export/", views.DataExportView.as_view(), name="data-export"),
    path("me/delete-account/", views.AccountDeleteView.as_view(), name="delete-account"),
    path("onboarding/", views.OnboardingView.as_view(), name="onboarding"),
    path("", include(router.urls)),
]
