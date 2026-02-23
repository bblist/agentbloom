import uuid
from django.db import models
from django.utils import timezone


class Service(models.Model):
    """Bookable service (e.g., "HVAC Repair", "Yoga Class")."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=60)  # minutes
    buffer_before = models.IntegerField(default=0)  # minutes buffer before
    buffer_after = models.IntegerField(default=15)  # minutes buffer after
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    color = models.CharField(max_length=7, default="#3B82F6")  # Hex color
    max_bookings_per_slot = models.IntegerField(default=1)
    is_group = models.BooleanField(default=False)
    max_group_size = models.IntegerField(default=1)
    requires_confirmation = models.BooleanField(default=False)
    # Cancellation policy
    cancellation_window_hours = models.IntegerField(default=24)  # Hours before appt
    allow_reschedule = models.BooleanField(default=True)
    no_show_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Payment at booking
    require_payment = models.BooleanField(default=False)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 0 = full price
    stripe_price_id = models.CharField(max_length=255, blank=True)
    # Booking page
    booking_page_slug = models.SlugField(max_length=255, blank=True)  # Public booking page URL
    booking_page_description = models.TextField(blank=True)
    booking_page_image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services"

    def __str__(self):
        return f"{self.name} ({self.duration}min)"


class AvailabilitySchedule(models.Model):
    """Weekly availability schedule for a service or staff member."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="availability_schedules")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name="schedules")
    staff = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, related_name="availability")
    name = models.CharField(max_length=255, default="Default Schedule")
    timezone = models.CharField(max_length=100, default="UTC")
    # Weekly schedule: {0: [{start: "09:00", end: "17:00"}], 1: [...], ...}
    weekly_hours = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "availability_schedules"

    def __str__(self):
        return self.name


class BlockedDate(models.Model):
    """Blocked date / time-off."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(AvailabilitySchedule, on_delete=models.CASCADE, related_name="blocked_dates")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)  # null = full day blocked
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "blocked_dates"


class Booking(models.Model):
    """A booking / appointment."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("no_show", "No Show"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50, blank=True)
    contact = models.ForeignKey("email_crm.Contact", on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    google_event_id = models.CharField(max_length=255, blank=True)
    reminder_sent = models.BooleanField(default=False)
    # Payment
    payment_status = models.CharField(max_length=50, choices=[
        ("none", "None"),
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
    ], default="none")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    series = models.ForeignKey("BookingSeries", on_delete=models.SET_NULL, null=True, blank=True)
    # Reschedule tracking
    rescheduled_from = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    reschedule_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookings"
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["org", "start_time"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.customer_name} — {self.service.name} @ {self.start_time}"


class BookingSeries(models.Model):
    """Recurring booking series."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    recurrence_rule = models.CharField(max_length=255)  # RRULE format
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "booking_series"
        verbose_name_plural = "booking series"


class Event(models.Model):
    """Group event (workshop, class, webinar)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=500, blank=True)
    is_virtual = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True)
    max_attendees = models.IntegerField(default=0)  # 0 = unlimited
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "events"
        ordering = ["start_time"]


class EventRegistration(models.Model):
    """Registration for a group event."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, choices=[
        ("registered", "Registered"),
        ("waitlisted", "Waitlisted"),
        ("cancelled", "Cancelled"),
        ("attended", "Attended"),
    ], default="registered")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "event_registrations"


class GoogleCalendarConnection(models.Model):
    """OAuth connection to Google Calendar for 2-way sync."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="google_calendars")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="google_calendars")
    calendar_id = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expires_at = models.DateTimeField()
    sync_token = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "google_calendar_connections"


class Waitlist(models.Model):
    """Waitlist entry for fully-booked services/events."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="waitlists")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name="waitlist")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name="waitlist")
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50, blank=True)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ("waiting", "Waiting"),
        ("notified", "Notified"),
        ("booked", "Booked"),
        ("expired", "Expired"),
    ], default="waiting")
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "waitlists"
        ordering = ["created_at"]


class BookingAnalytics(models.Model):
    """Aggregated booking analytics per service per period."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="booking_analytics")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="analytics")
    period = models.DateField()  # Month start
    total_bookings = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)
    cancelled = models.IntegerField(default=0)
    no_shows = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_rating = models.FloatField(default=0)
    popular_times = models.JSONField(default=dict, blank=True)  # {hour: count}
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "booking_analytics"
        unique_together = ("org", "service", "period")
        ordering = ["-period"]
