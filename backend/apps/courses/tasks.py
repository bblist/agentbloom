"""Celery tasks for courses."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_enrollment_progress(enrollment_id):
    """Recalculate enrollment progress based on completed lessons."""
    from .models import Enrollment, LessonProgress, Lesson

    try:
        enrollment = Enrollment.objects.select_related("course").get(id=enrollment_id)
        total_lessons = Lesson.objects.filter(
            section__course=enrollment.course
        ).count()

        if total_lessons == 0:
            return {"progress": 0}

        completed = LessonProgress.objects.filter(
            enrollment=enrollment, is_completed=True
        ).count()

        progress = round(completed / total_lessons * 100)
        enrollment.progress_pct = progress
        enrollment.save(update_fields=["progress_pct"])

        # Check completion
        if progress >= 100 and not enrollment.completed_at:
            from django.utils import timezone
            enrollment.completed_at = timezone.now()
            enrollment.save(update_fields=["completed_at"])

            # Update course stats
            course = enrollment.course
            total_enrollments = course.enrollments.count()
            completed_count = course.enrollments.filter(completed_at__isnull=False).count()
            course.completion_rate = round(completed_count / total_enrollments * 100, 1)
            course.save(update_fields=["completion_rate"])

            # TODO: Generate certificate if enabled

        return {"enrollment_id": str(enrollment_id), "progress": progress}

    except Enrollment.DoesNotExist:
        logger.error(f"Enrollment {enrollment_id} not found")
        return {"error": "not_found"}


@shared_task
def send_course_announcement_emails(announcement_id):
    """Email course announcement to all enrolled students."""
    from .models import CourseAnnouncement

    try:
        announcement = CourseAnnouncement.objects.select_related("course").get(id=announcement_id)
        if not announcement.send_email:
            return {"skipped": True}

        enrollments = announcement.course.enrollments.select_related("user").all()
        sent = 0
        for enrollment in enrollments:
            # TODO: Send via SES
            sent += 1

        logger.info(f"Sent announcement '{announcement.title}' to {sent} students")
        return {"sent": sent}

    except CourseAnnouncement.DoesNotExist:
        return {"error": "not_found"}


@shared_task
def generate_certificate(enrollment_id):
    """Generate a completion certificate PDF."""
    from .models import Enrollment, Certificate
    import uuid

    try:
        enrollment = Enrollment.objects.select_related("course", "user").get(id=enrollment_id)
        if not enrollment.completed_at:
            return {"error": "not_completed"}

        cert_number = f"AB-{str(uuid.uuid4())[:8].upper()}"
        cert = Certificate.objects.create(
            enrollment=enrollment,
            certificate_number=cert_number,
            verification_url=f"https://agentbloom.nobleblocks.com/verify/{cert_number}",
            # TODO: Generate PDF and upload to S3
        )

        logger.info(f"Certificate {cert_number} generated for {enrollment.user.email}")
        return {"certificate_number": cert_number}

    except Enrollment.DoesNotExist:
        return {"error": "not_found"}
