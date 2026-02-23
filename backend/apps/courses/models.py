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

    MODE_CHOICES = [
        ("self_paced", "Self-Paced"),
        ("cohort", "Cohort-Based"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    promo_video_url = models.URLField(blank=True)  # Course preview video
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    mode = models.CharField(max_length=50, choices=MODE_CHOICES, default="self_paced")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    is_free = models.BooleanField(default=False)
    drip_enabled = models.BooleanField(default=False)
    certificate_enabled = models.BooleanField(default=False)
    enrollment_count = models.IntegerField(default=0)
    # Completion requirements
    require_sequential = models.BooleanField(default=False)  # Must complete in order
    passing_grade = models.IntegerField(default=70)  # Min % to pass
    # Cohort settings
    cohort_start_date = models.DateField(null=True, blank=True)
    cohort_end_date = models.DateField(null=True, blank=True)
    max_enrollment = models.IntegerField(default=0)  # 0 = unlimited
    # Analytics
    completion_rate = models.FloatField(default=0)
    avg_rating = models.FloatField(default=0)
    revenue_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
    # Prerequisites
    prerequisite_section = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="dependent_sections"
    )
    is_locked = models.BooleanField(default=False)  # Manually locked
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
        ("live_session", "Live Session"),
        ("download", "Downloadable Resource"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES, default="video")
    content = models.TextField(blank=True)  # Rich text or markdown
    video_url = models.URLField(blank=True)  # CloudFront HLS URL
    video_duration = models.IntegerField(default=0)  # seconds
    # Video player features
    captions_url = models.URLField(blank=True)  # Auto-generated captions (Whisper)
    transcript = models.TextField(blank=True)  # Full text transcript
    file_url = models.URLField(blank=True)  # PDF or file download
    is_preview = models.BooleanField(default=False)  # Free preview
    # Live session support (cohort mode)
    live_session_url = models.URLField(blank=True)  # Zoom/Google Meet embed
    live_session_at = models.DateTimeField(null=True, blank=True)
    # Completion tracking
    estimated_duration = models.IntegerField(default=0)  # minutes
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
    show_correct_answers = models.BooleanField(default=True)
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
        ("matching", "Matching"),
        ("fill_blank", "Fill in the Blank"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, default="multiple_choice")
    options = models.JSONField(default=list, blank=True)  # [{text, is_correct}]
    correct_answer = models.TextField(blank=True)  # For short_answer / fill_blank
    points = models.IntegerField(default=1)
    explanation = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "quiz_questions"
        ordering = ["sort_order"]


class QuizAttempt(models.Model):
    """Student quiz attempt with scoring."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE, related_name="quiz_attempts")
    answers = models.JSONField(default=dict)  # {question_id: answer}
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    time_spent = models.IntegerField(default=0)  # seconds
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "quiz_attempts"
        ordering = ["-started_at"]


class Assignment(models.Model):
    """Assignment for student submissions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="assignment")
    instructions = models.TextField()
    max_file_size_mb = models.IntegerField(default=50)
    allowed_file_types = models.JSONField(default=list, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    max_points = models.IntegerField(default=100)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "assignments"


class AssignmentSubmission(models.Model):
    """Student submission for an assignment."""

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
        ("returned", "Returned for Revision"),
        ("graded", "Graded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE, related_name="assignment_submissions")
    content = models.TextField(blank=True)
    file_urls = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="submitted")
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "assignment_submissions"
        ordering = ["-submitted_at"]


class Enrollment(models.Model):
    """Student enrollment in a course."""

    SOURCE_CHOICES = [
        ("direct", "Direct"),
        ("invite", "Invite"),
        ("bulk", "Bulk Import"),
        ("promo", "Promo Code"),
        ("membership", "Membership"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="enrollments")
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="direct")
    progress_pct = models.IntegerField(default=0)
    enrolled_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    # Time tracking
    total_time_spent = models.IntegerField(default=0)  # seconds
    # Engagement
    engagement_score = models.IntegerField(default=0)  # 0-100

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
    # Video bookmarks and notes
    bookmarks = models.JSONField(default=list, blank=True)  # [{time_seconds, label}]
    notes = models.TextField(blank=True)
    last_position = models.IntegerField(default=0)  # Video position in seconds
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "lesson_progress"
        unique_together = ("enrollment", "lesson")


class Certificate(models.Model):
    """Certificate issued upon course completion."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="certificate")
    certificate_number = models.CharField(max_length=100, unique=True)
    template = models.ForeignKey("CertificateTemplate", on_delete=models.SET_NULL, null=True, blank=True)
    pdf_url = models.URLField(blank=True)
    verification_url = models.URLField(blank=True)  # Unique verification URL
    issued_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "certificates"


class CertificateTemplate(models.Model):
    """Custom certificate template for PDF generation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="certificate_templates")
    name = models.CharField(max_length=255)
    html_template = models.TextField()  # HTML template with merge fields
    background_image_url = models.URLField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "certificate_templates"


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
    # Access rules
    access_rules = models.JSONField(default=list, blank=True)  # [{type, resource_id, ...}]
    stripe_price_id = models.CharField(max_length=255, blank=True)
    # Member benefits
    resources = models.JSONField(default=list, blank=True)  # [{title, file_url, description}]
    welcome_email_template = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    member_count = models.IntegerField(default=0)
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
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, choices=[
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
        ("past_due", "Past Due"),
    ], default="active")
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    # Engagement
    engagement_score = models.IntegerField(default=0)
    last_active = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)

    class Meta:
        db_table = "memberships"


class MemberProfile(models.Model):
    """Extended member profile for community features."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="member_profile")
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="member_profiles")
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    is_public = models.BooleanField(default=False)  # Show in member directory
    # Gamification
    points = models.IntegerField(default=0)
    badges = models.JSONField(default=list, blank=True)  # [{name, icon, earned_at}]
    streak_days = models.IntegerField(default=0)
    streak_last_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "member_profiles"
        unique_together = ("user", "org")


class CommunitySpace(models.Model):
    """Community discussion space for a course or membership."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="community_spaces")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    membership_tier = models.ForeignKey(MembershipTier, on_delete=models.SET_NULL, null=True, blank=True)
    space_type = models.CharField(max_length=50, choices=[
        ("discussion", "Discussion"),
        ("announcement", "Announcements"),
        ("qa", "Q&A"),
        ("showcase", "Showcase"),
    ], default="discussion")
    is_active = models.BooleanField(default=True)
    member_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "community_spaces"


class CommunityPost(models.Model):
    """Post in a community space — activity-feed style (not threaded forum)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(CommunitySpace, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="community_posts")
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    content_type = models.CharField(max_length=50, choices=[
        ("text", "Text"),
        ("image", "Image"),
        ("poll", "Poll"),
        ("link", "Link"),
    ], default="text")
    media_urls = models.JSONField(default=list, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    is_pinned = models.BooleanField(default=False)
    is_announcement = models.BooleanField(default=False)
    # Engagement
    reaction_count = models.IntegerField(default=0)
    reactions = models.JSONField(default=dict, blank=True)  # {"like": 5, "heart": 3, ...}
    reply_count = models.IntegerField(default=0)
    mentions = models.JSONField(default=list, blank=True)  # [user_id, ...]
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "community_posts"
        ordering = ["-is_pinned", "-created_at"]


class CourseAnnouncement(models.Model):
    """Announcement to enrolled students."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="announcements")
    author = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    send_email = models.BooleanField(default=True)  # Also email to enrolled students
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "course_announcements"
        ordering = ["-created_at"]


class CourseReview(models.Model):
    """Student review of a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="review")
    rating = models.IntegerField()  # 1-5
    review = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "course_reviews"
        ordering = ["-created_at"]


class BulkEnrollment(models.Model):
    """Bulk enrollment job (CSV import, invite link, promo code)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="bulk_enrollments")
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    method = models.CharField(max_length=50, choices=[
        ("csv", "CSV Import"),
        ("invite_link", "Invite Link"),
        ("promo_code", "Promo Code"),
    ])
    data = models.JSONField(default=dict)  # CSV data or invite/promo config
    enrolled_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=50, choices=[
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ], default="processing")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "bulk_enrollments"
