from django.contrib import admin
from .models import Course, CourseSection, Lesson, Quiz, Enrollment, MembershipTier, CommunitySpace


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "org", "status", "price", "enrollment_count", "created_at")
    list_filter = ("status", "is_free")
    search_fields = ("title",)


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "sort_order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "content_type", "is_preview", "sort_order")
    list_filter = ("content_type", "is_preview")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "passing_score", "max_attempts")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "progress_pct", "enrolled_at")


@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "price", "billing_period", "is_active")


@admin.register(CommunitySpace)
class CommunitySpaceAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "course", "is_active")
