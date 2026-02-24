from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone

from .models import (
    Course, CourseSection, Lesson, Quiz, QuizQuestion, QuizAttempt,
    Assignment, AssignmentSubmission, Enrollment, LessonProgress,
    Certificate, CertificateTemplate, MembershipTier, Membership,
    CommunitySpace, CommunityPost, CourseAnnouncement, CourseReview,
)
from .serializers import (
    CourseListSerializer, CourseDetailSerializer, CourseSectionSerializer,
    LessonSerializer, QuizSerializer, QuizQuestionSerializer,
    QuizAttemptSerializer, AssignmentSerializer, AssignmentSubmissionSerializer,
    EnrollmentSerializer, LessonProgressSerializer,
    CertificateSerializer, CertificateTemplateSerializer,
    MembershipTierSerializer, MembershipSerializer,
    CommunitySpaceSerializer, CommunityPostSerializer,
    CourseAnnouncementSerializer, CourseReviewSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD for courses. Nested sections / lessons loaded via detail."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Course.objects.filter(org=self.request.org)
            .annotate(
                section_count=Count("sections", distinct=True),
                lesson_count=Count("sections__lessons", distinct=True),
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseDetailSerializer

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        course = self.get_object()
        if course.sections.count() == 0:
            return Response({"error": "Add at least one section before publishing."}, status=400)
        course.status = "published"
        course.save(update_fields=["status", "updated_at"])
        return Response({"status": "published"})

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        course = self.get_object()
        course.status = "archived"
        course.save(update_fields=["status", "updated_at"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        course = self.get_object()
        enrollments = course.enrollments.all()
        return Response({
            "total_enrolled": enrollments.count(),
            "completed": enrollments.filter(completed_at__isnull=False).count(),
            "avg_progress": enrollments.values_list("progress_pct", flat=True),
            "revenue": float(course.revenue_total),
            "avg_rating": course.avg_rating,
        })


class CourseSectionViewSet(viewsets.ModelViewSet):
    """Sections within a course (nested under /courses/{id}/sections/)."""
    serializer_class = CourseSectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseSection.objects.filter(
            course__org=self.request.org,
            course_id=self.kwargs["course_pk"],
        )

    def perform_create(self, serializer):
        serializer.save(course_id=self.kwargs["course_pk"])

    @action(detail=True, methods=["post"])
    def reorder(self, request, course_pk=None, pk=None):
        section = self.get_object()
        new_order = request.data.get("sort_order", 0)
        section.sort_order = new_order
        section.save(update_fields=["sort_order"])
        return Response({"sort_order": new_order})


class LessonViewSet(viewsets.ModelViewSet):
    """Lessons within a section (nested under sections/{id}/lessons/)."""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.filter(
            section__course__org=self.request.org,
            section_id=self.kwargs["section_pk"],
        )

    def perform_create(self, serializer):
        serializer.save(section_id=self.kwargs["section_pk"])


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(lesson__section__course__org=self.request.org)


class QuizQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizQuestion.objects.filter(
            quiz_id=self.kwargs["quiz_pk"],
            quiz__lesson__section__course__org=self.request.org,
        )

    def perform_create(self, serializer):
        serializer.save(quiz_id=self.kwargs["quiz_pk"])


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(course__org=self.request.org).select_related("course", "user")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.completed_at = timezone.now()
        enrollment.progress_pct = 100
        enrollment.save(update_fields=["completed_at", "progress_pct"])
        return Response({"status": "completed"})


class LessonProgressViewSet(viewsets.ModelViewSet):
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head"]

    def get_queryset(self):
        return LessonProgress.objects.filter(
            enrollment__course__org=self.request.org
        )


class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(
            quiz__lesson__section__course__org=self.request.org
        )

    def perform_create(self, serializer):
        """Auto-grade quiz attempt on submission."""
        attempt = serializer.save()
        quiz = attempt.quiz
        questions = quiz.questions.all()
        total, score = 0, 0
        for q in questions:
            total += q.points
            student_answer = attempt.answers.get(str(q.id))
            if q.question_type in ("multiple_choice", "true_false"):
                correct_idx = next(
                    (i for i, o in enumerate(q.options) if o.get("is_correct")), None
                )
                if student_answer == correct_idx or student_answer == str(correct_idx):
                    score += q.points
            elif q.question_type in ("short_answer", "fill_blank"):
                if str(student_answer).strip().lower() == q.correct_answer.strip().lower():
                    score += q.points
        pct = round(score / total * 100) if total else 0
        attempt.score = score
        attempt.max_score = total
        attempt.percentage = pct
        attempt.passed = pct >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assignment.objects.filter(lesson__section__course__org=self.request.org)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AssignmentSubmission.objects.filter(
            assignment__lesson__section__course__org=self.request.org
        )

    @action(detail=True, methods=["post"])
    def grade(self, request, pk=None):
        submission = self.get_object()
        submission.grade = request.data.get("grade")
        submission.feedback = request.data.get("feedback", "")
        submission.status = "graded"
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save()
        return Response(AssignmentSubmissionSerializer(submission).data)


class CertificateTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = CertificateTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CertificateTemplate.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class MembershipTierViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipTierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MembershipTier.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Membership.objects.filter(tier__org=self.request.org).select_related("tier")


class CommunitySpaceViewSet(viewsets.ModelViewSet):
    serializer_class = CommunitySpaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CommunitySpace.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class CommunityPostViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CommunityPost.objects.filter(
            space__org=self.request.org,
            space_id=self.kwargs.get("space_pk"),
        ).select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def react(self, request, space_pk=None, pk=None):
        post = self.get_object()
        reaction = request.data.get("reaction", "like")
        reactions = post.reactions or {}
        reactions[reaction] = reactions.get(reaction, 0) + 1
        post.reactions = reactions
        post.reaction_count = sum(reactions.values())
        post.save(update_fields=["reactions", "reaction_count"])
        return Response({"reactions": reactions})


class CourseAnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = CourseAnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseAnnouncement.objects.filter(course__org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CourseReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        return CourseReview.objects.filter(course__org=self.request.org)
