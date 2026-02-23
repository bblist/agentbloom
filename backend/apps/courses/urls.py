from django.urls import path, include
from rest_framework.routers import DefaultRouter

# TODO: Create viewsets for courses, enrollments, quizzes, memberships, community
# router = DefaultRouter()
# router.register(r"courses", views.CourseViewSet, basename="course")
# router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
# router.register(r"membership-tiers", views.MembershipTierViewSet, basename="membership-tier")

urlpatterns = [
    # path("", include(router.urls)),
]
