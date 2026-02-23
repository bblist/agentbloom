from django.contrib import admin
from .models import Service, AvailabilitySchedule, Booking, Event, EventRegistration, GoogleCalendarConnection


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "duration", "price", "is_active")
    list_filter = ("is_active", "is_group")


@admin.register(AvailabilitySchedule)
class AvailabilityScheduleAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "service", "staff", "is_default")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "service", "start_time", "status")
    list_filter = ("status",)
    search_fields = ("customer_name", "customer_email")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "org", "start_time", "max_attendees", "is_active")


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "status", "created_at")
    list_filter = ("status",)


@admin.register(GoogleCalendarConnection)
class GoogleCalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ("org", "user", "calendar_id", "is_active", "last_synced")
