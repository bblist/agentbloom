import uuid
from django.db import models
from django.utils import timezone


class Course(models.Model):
    """Online course."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    is_free = models.BooleanField(default=False)
    drip_enabled = models.BooleanField(default=False)
    certificate_enabled = models.BooleanField(default=False)
    enrollment_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        unique_together = ("org", "slug")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class CourseSection(models.Model):
    """Section / module within a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    drip_days = models.IntegerField(default=0)  # Days after enrollment to unlock
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "course_sections"
        ordering = ["sort_order"]


class Lesson(models.Model):
    """Lesson within a section."""

    CONTENT_TYPES = [
        ("video", "Video"),
        ("text", "Text"),
        ("pdf", "PDF"),
        ("quiz", "Quiz"),
        ("assignment", "Assignment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES, default="video")
    content = models.TextField(blank=True)  # Rich text or markdown
    video_url = models.URLField(blank=True)  # CloudFront HLS URL
    video_duration = models.IntegerField(default=0)  # seconds
    file_url = models.URLField(blank=True)  # PDF or file download
    is_preview = models.BooleanField(default=False)  # Free preview
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        ordering = ["sort_order"]


class Quiz(models.Model):
    """Quiz attached to a lesson or course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=255)
    passing_score = models.IntegerField(default=70)  # percentage
    time_limit = models.IntegerField(default=0)  # minutes, 0 = no limit
    max_attempts = models.IntegerField(default=0)  # 0 = unlimited
    randomize = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "quizzes"
        verbose_name_plural = "quizzes"


class QuizQuestion(models.Model):
    """Question within a quiz."""

    QUESTION_TYPES = [
        ("multiple_choice", "Multiple Choice"),
        ("true_false", "True/False"),
        ("short_answer", "Short Answer"),
        ("essay", "Essay"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, default="multiple_choice")
    options = models.JSONField(default=list, blank=True)  # [{text, is_correct}]
    correct_answer = models.TextField(blank=True)  # For short_answer
    points = models.IntegerField(default=1)
    explanation = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "quiz_questions"
        ordering = ["sort_order"]


class Enrollment(models.Model):
    """Student enrollment in a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="enrollments")
    progress_pct = models.IntegerField(default=0)
    enrolled_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "enrollments"
        unique_together = ("course", "user")

    def __str__(self):
        return f"{self.user.email} in {self.course.title}"


class LessonProgress(models.Model):
    """Track completion of individual lessons."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    watch_time = models.IntegerField(default=0)  # seconds
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lesson_progress"
        unique_together = ("enrollment", "lesson")


class Certificate(models.Model):
    """Certificate issued upon course completion."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="certificate")
    certificate_number = models.CharField(max_length=100, unique=True)
    pdf_url = models.URLField(blank=True)
    issued_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "certificates"


class MembershipTier(models.Model):
    """Membership tier / access level."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="membership_tiers")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    billing_period = models.CharField(max_length=50, choices=[
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("one_time", "One Time"),
    ], default="monthly")
    courses = models.ManyToManyField(Course, blank=True, related_name="membership_tiers")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "membership_tiers"

    def __str__(self):
        return f"{self.name} — ${self.price}/{self.billing_period}"


class Membership(models.Model):
    """User membership in a tier."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="memberships_course")
    tier = models.ForeignKey(MembershipTier, on_delete=models.CASCADE, related_name="members")
    status = models.CharField(max_length=50, choices=[
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ], default="active")
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "memberships"


class CommunitySpace(models.Model):
    """Community discussion space for a course or membership."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="community_spaces")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "community_spaces"


class CommunityPost(models.Model):
    """Post in a community space."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(CommunitySpace, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="community_posts")
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    is_pinned = models.BooleanField(default=False)
    reaction_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "community_posts"
        ordering = ["-is_pinned", "-created_at"]
