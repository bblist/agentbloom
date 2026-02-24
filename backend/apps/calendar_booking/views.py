from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime

from .models import (
    Service, AvailabilitySchedule, BlockedDate, Booking, BookingSeries,
    Event, EventRegistration, GoogleCalendarConnection, Waitlist,
)
from .serializers import (
    ServiceSerializer, AvailabilityScheduleSerializer, BlockedDateSerializer,
    BookingSerializer, BookingCreateSerializer, BookingSeriesSerializer,
    EventSerializer, EventRegistrationSerializer,
    GoogleCalendarConnectionSerializer, WaitlistSerializer,
)


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Service.objects.filter(org=self.request.org).annotate(
            booking_count=Count("bookings"),
        )

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def available_slots(self, request, pk=None):
        """Return available time slots for a service on a given date."""
        service = self.get_object()
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "date query param required (YYYY-MM-DD)"}, status=400)

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format"}, status=400)

        # Get schedule
        schedule = service.schedules.filter(is_default=True).first()
        if not schedule:
            schedule = AvailabilitySchedule.objects.filter(
                org=service.org, is_default=True, service__isnull=True
            ).first()

        if not schedule or not schedule.weekly_hours:
            return Response({"slots": []})

        weekday = str(target_date.weekday())
        day_hours = schedule.weekly_hours.get(weekday, [])
        if not day_hours:
            return Response({"slots": []})

        # Check blocked dates
        blocked = schedule.blocked_dates.filter(date=target_date)
        full_day_blocked = blocked.filter(start_time__isnull=True).exists()
        if full_day_blocked:
            return Response({"slots": []})

        # Get existing bookings for this date
        day_start = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
        day_end = day_start + timedelta(days=1)
        existing = Booking.objects.filter(
            service=service,
            start_time__gte=day_start,
            start_time__lt=day_end,
            status__in=["pending", "confirmed"],
        ).values_list("start_time", "end_time")

        slots = []
        duration = timedelta(minutes=service.duration)
        buffer = timedelta(minutes=service.buffer_before + service.buffer_after)

        for window in day_hours:
            start = timezone.make_aware(
                datetime.combine(target_date, datetime.strptime(window["start"], "%H:%M").time())
            )
            end = timezone.make_aware(
                datetime.combine(target_date, datetime.strptime(window["end"], "%H:%M").time())
            )
            current = start
            while current + duration <= end:
                slot_end = current + duration
                conflict = any(
                    current < b_end and slot_end > b_start
                    for b_start, b_end in existing
                )
                if not conflict:
                    slots.append({
                        "start": current.isoformat(),
                        "end": slot_end.isoformat(),
                        "available": True,
                    })
                current += duration + buffer

        return Response({"slots": slots})


class AvailabilityScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilityScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AvailabilitySchedule.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class BlockedDateViewSet(viewsets.ModelViewSet):
    serializer_class = BlockedDateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BlockedDate.objects.filter(schedule__org=self.request.org)


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Booking.objects.filter(org=self.request.org).select_related("service")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        date_from = self.request.query_params.get("from")
        date_to = self.request.query_params.get("to")
        if date_from:
            qs = qs.filter(start_time__gte=date_from)
        if date_to:
            qs = qs.filter(start_time__lte=date_to)
        return qs

    def get_serializer_class(self):
        if self.action == "create" and not self.request.user.is_authenticated:
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        service = serializer.validated_data["service"]
        # Auto-calculate end_time if not provided
        start = serializer.validated_data["start_time"]
        end = serializer.validated_data.get("end_time") or start + timedelta(minutes=service.duration)
        booking_status = "confirmed" if not service.requires_confirmation else "pending"
        serializer.save(org=self.request.org, end_time=end, status=booking_status)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.status = "cancelled"
        booking.cancellation_reason = request.data.get("reason", "")
        booking.save(update_fields=["status", "cancellation_reason", "updated_at"])
        return Response({"status": "cancelled"})

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        booking.status = "confirmed"
        booking.save(update_fields=["status", "updated_at"])
        return Response({"status": "confirmed"})

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        booking = self.get_object()
        new_start = request.data.get("start_time")
        if not new_start:
            return Response({"error": "start_time required"}, status=400)
        old_booking = booking
        new_end = request.data.get("end_time")
        if not new_end:
            new_start_dt = datetime.fromisoformat(new_start)
            new_end = (new_start_dt + timedelta(minutes=booking.service.duration)).isoformat()
        booking.start_time = new_start
        booking.end_time = new_end
        booking.reschedule_count += 1
        booking.save(update_fields=["start_time", "end_time", "reschedule_count", "updated_at"])
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=["post"])
    def no_show(self, request, pk=None):
        booking = self.get_object()
        booking.status = "no_show"
        booking.save(update_fields=["status", "updated_at"])
        return Response({"status": "no_show"})

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def public_book(self, request):
        """Public booking endpoint — no auth required."""
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.validated_data["service"]
        start = serializer.validated_data["start_time"]
        end = serializer.validated_data.get("end_time") or start + timedelta(minutes=service.duration)
        booking_status = "confirmed" if not service.requires_confirmation else "pending"
        booking = serializer.save(org=service.org, end_time=end, status=booking_status)
        return Response(BookingSerializer(booking).data, status=201)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(org=self.request.org).annotate(
            registration_count=Count("registrations"),
        )

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EventRegistration.objects.filter(event__org=self.request.org)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def public_register(self, request):
        """Public event registration."""
        serializer = EventRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.validated_data["event"]
        if event.max_attendees > 0:
            current = event.registrations.filter(status="registered").count()
            if current >= event.max_attendees:
                serializer.validated_data["status"] = "waitlisted"
        serializer.save()
        return Response(serializer.data, status=201)


class WaitlistViewSet(viewsets.ModelViewSet):
    serializer_class = WaitlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Waitlist.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class GoogleCalendarConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = GoogleCalendarConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoogleCalendarConnection.objects.filter(org=self.request.org)
