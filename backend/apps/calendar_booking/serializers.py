from rest_framework import serializers
from .models import (
    Service, AvailabilitySchedule, BlockedDate, Booking, BookingSeries,
    Event, EventRegistration, GoogleCalendarConnection, Waitlist,
)


class ServiceSerializer(serializers.ModelSerializer):
    booking_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at", "updated_at")


class BlockedDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedDate
        fields = "__all__"
        read_only_fields = ("id",)


class AvailabilityScheduleSerializer(serializers.ModelSerializer):
    blocked_dates = BlockedDateSerializer(many=True, read_only=True)

    class Meta:
        model = AvailabilitySchedule
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at", "updated_at")


class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = (
            "id", "org", "google_event_id", "reminder_sent",
            "reschedule_count", "created_at", "updated_at",
        )


class BookingCreateSerializer(serializers.ModelSerializer):
    """Public booking creation — minimal required fields."""
    class Meta:
        model = Booking
        fields = [
            "service", "customer_name", "customer_email",
            "customer_phone", "start_time", "end_time", "notes",
        ]


class BookingSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSeries
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at")


class EventSerializer(serializers.ModelSerializer):
    registration_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at")


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class GoogleCalendarConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleCalendarConnection
        fields = [
            "id", "calendar_id", "is_active", "last_synced", "created_at",
        ]
        read_only_fields = ("id", "created_at")


class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = "__all__"
        read_only_fields = ("id", "org", "notified_at", "created_at")


class AvailabilitySlotSerializer(serializers.Serializer):
    """Output serializer for available time slots."""
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    available = serializers.BooleanField(default=True)
