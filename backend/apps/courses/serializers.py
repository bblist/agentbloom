from rest_framework import serializers
from .models import (
    Course, CourseSection, Lesson, Quiz, QuizQuestion, QuizAttempt,
    Assignment, AssignmentSubmission, Enrollment, LessonProgress,
    Certificate, CertificateTemplate, MembershipTier, Membership,
    CommunitySpace, CommunityPost, CourseAnnouncement, CourseReview,
)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = "__all__"
        read_only_fields = ("id",)


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class CourseSectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = CourseSection
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class CourseListSerializer(serializers.ModelSerializer):
    section_count = serializers.IntegerField(read_only=True, default=0)
    lesson_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description", "thumbnail_url",
            "status", "mode", "price", "currency", "is_free",
            "enrollment_count", "completion_rate", "avg_rating",
            "section_count", "lesson_count", "created_at",
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    sections = CourseSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = (
            "id", "org", "enrollment_count", "completion_rate",
            "avg_rating", "revenue_total", "created_at", "updated_at",
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = (
            "id", "progress_pct", "enrolled_at", "completed_at",
            "total_time_spent", "engagement_score",
        )


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = "__all__"
        read_only_fields = ("id",)


class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = "__all__"
        read_only_fields = (
            "id", "score", "max_score", "percentage", "passed",
            "started_at", "completed_at",
        )


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = "__all__"
        read_only_fields = ("id", "submitted_at", "graded_at")


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"
        read_only_fields = ("id", "certificate_number", "issued_at")


class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateTemplate
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class MembershipTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipTier
        fields = "__all__"
        read_only_fields = ("id", "member_count", "created_at")


class MembershipSerializer(serializers.ModelSerializer):
    tier_name = serializers.CharField(source="tier.name", read_only=True)

    class Meta:
        model = Membership
        fields = "__all__"
        read_only_fields = ("id", "started_at")


class CommunitySpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunitySpace
        fields = "__all__"
        read_only_fields = ("id", "member_count", "created_at")


class CommunityPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True, default="")

    class Meta:
        model = CommunityPost
        fields = "__all__"
        read_only_fields = (
            "id", "author", "reaction_count", "reply_count",
            "created_at", "updated_at",
        )


class CourseAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAnnouncement
        fields = "__all__"
        read_only_fields = ("id", "author", "created_at")


class CourseReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = CourseReview
        fields = "__all__"
        read_only_fields = ("id", "enrollment", "created_at")

    def get_user_name(self, obj):
        try:
            return obj.enrollment.user.full_name or obj.enrollment.user.email
        except Exception:
            return ""
