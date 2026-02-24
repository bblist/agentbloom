from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views

router = DefaultRouter()
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"lesson-progress", views.LessonProgressViewSet, basename="lesson-progress")
router.register(r"quizzes", views.QuizViewSet, basename="quiz")
router.register(r"quiz-attempts", views.QuizAttemptViewSet, basename="quiz-attempt")
router.register(r"assignments", views.AssignmentViewSet, basename="assignment")
router.register(r"assignment-submissions", views.AssignmentSubmissionViewSet, basename="assignment-submission")
router.register(r"certificate-templates", views.CertificateTemplateViewSet, basename="certificate-template")
router.register(r"membership-tiers", views.MembershipTierViewSet, basename="membership-tier")
router.register(r"memberships", views.MembershipViewSet, basename="membership")
router.register(r"community-spaces", views.CommunitySpaceViewSet, basename="community-space")
router.register(r"announcements", views.CourseAnnouncementViewSet, basename="announcement")
router.register(r"reviews", views.CourseReviewViewSet, basename="review")

# Nested routes
courses_router = NestedDefaultRouter(router, r"courses", lookup="course")
courses_router.register(r"sections", views.CourseSectionViewSet, basename="course-section")

sections_router = NestedDefaultRouter(courses_router, r"sections", lookup="section")
sections_router.register(r"lessons", views.LessonViewSet, basename="section-lesson")

quizzes_router = NestedDefaultRouter(router, r"quizzes", lookup="quiz")
quizzes_router.register(r"questions", views.QuizQuestionViewSet, basename="quiz-question")

spaces_router = NestedDefaultRouter(router, r"community-spaces", lookup="space")
spaces_router.register(r"posts", views.CommunityPostViewSet, basename="space-post")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(courses_router.urls)),
    path("", include(sections_router.urls)),
    path("", include(quizzes_router.urls)),
    path("", include(spaces_router.urls)),
]
