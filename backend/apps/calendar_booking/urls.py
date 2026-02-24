from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"services", views.ServiceViewSet, basename="service")
router.register(r"availability", views.AvailabilityScheduleViewSet, basename="availability")
router.register(r"blocked-dates", views.BlockedDateViewSet, basename="blocked-date")
router.register(r"bookings", views.BookingViewSet, basename="booking")
router.register(r"events", views.EventViewSet, basename="event")
router.register(r"event-registrations", views.EventRegistrationViewSet, basename="event-registration")
router.register(r"waitlist", views.WaitlistViewSet, basename="waitlist")
router.register(r"google-calendar", views.GoogleCalendarConnectionViewSet, basename="google-calendar")

urlpatterns = [
    path("", include(router.urls)),
]
