# Phase 5 — Calendar & Booking

> **Goal**: Build the booking system with public booking pages, service types, availability management, and Google Calendar sync. After this phase, service businesses can accept online bookings.

## Status: NOT STARTED

## Dependencies
- Phase 0 (Foundation) — auth, DB
- Phase 2 (Dashboard) — UI shell
- Phase 3 (Email) — booking confirmation/reminder emails

## Checklist

### Service Management
- [ ] Service types: name, description, duration, price, capacity, color
- [ ] Service categories: group related services
- [ ] Intake questions: custom fields per service (text, dropdown, checkbox)
- [ ] Service images and descriptions
- [ ] Active/inactive toggle
- [ ] Sort order for display

### Availability Management
- [ ] Weekly schedule: set available hours per day of week
- [ ] Multiple schedules: different availability for different services
- [ ] Blocked dates: mark specific dates as unavailable (holidays, vacation)
- [ ] Buffer time: configurable gap between appointments (5-60 min)
- [ ] Notice period: minimum advance booking time (1 hour - 1 week)
- [ ] Maximum advance: how far ahead can they book (1 week - 6 months)
- [ ] Timezone handling: all times stored UTC, displayed in user/client timezone
- [ ] Slot calculation: available minus booked minus blocked minus buffer

### Public Booking Page
- [ ] Branded booking page: /book/[org-slug] or custom domain
- [ ] Service selection (if multiple)
- [ ] Calendar view: date picker showing available dates
- [ ] Time slot selection: available times for selected date
- [ ] Booking form: name, email, phone + custom intake fields
- [ ] Payment at booking (optional): full price or deposit (Stripe)
- [ ] Confirmation page: booking details, calendar download (.ics)
- [ ] Embeddable widget: iframe for user's existing website

### Google Calendar Integration
- [ ] OAuth connection to Google Calendar
- [ ] 2-way sync:
  - [ ] AgentBloom bookings → create Google Calendar event
  - [ ] Google Calendar events → block availability in AgentBloom
- [ ] Real-time sync (webhook-based via Google Calendar API push notifications)
- [ ] Support for multiple calendars (personal + work)
- [ ] Disconnect/reconnect flow

### Booking Management
- [ ] Booking list: upcoming, past, cancelled, with search/filter
- [ ] Booking detail: client info, service, time, status, notes, payment
- [ ] Status workflow: Pending → Confirmed → Completed / Cancelled / No-Show
- [ ] Manual booking: staff adds booking manually (for phone/walk-in)
- [ ] Reschedule: client self-service via link in confirmation email
- [ ] Cancel: client self-service with cancellation policy enforcement
- [ ] No-show tracking: mark no-shows, charge no-show fee (if configured)
- [ ] Notes: internal notes per booking

### Group Events / Classes
- [ ] Event creation: name, date/time, duration, capacity, price
- [ ] RSVP / registration page
- [ ] Waitlist: when capacity reached, auto-notify on cancellation
- [ ] Recurring events: weekly, biweekly, monthly
- [ ] Attendee list management
- [ ] Event reminders (email)

### Recurring Appointments
- [ ] Create recurring series: weekly, biweekly, monthly
- [ ] Manage individual instances (reschedule/cancel one without affecting series)
- [ ] Client recurring booking: "Book me for 8 weekly sessions"

### Reminders & Notifications
- [ ] Booking confirmation email (client + owner)
- [ ] Reminder emails: configurable timing (24h, 1h before)
- [ ] Reminder SMS (optional, via SNS or future Twilio)
- [ ] Cancellation notification email
- [ ] Reschedule notification email
- [ ] Follow-up email after appointment (automated)
- [ ] Calendar invites (.ics attachment)

### Booking Analytics
- [ ] Total bookings: daily, weekly, monthly
- [ ] Most popular services
- [ ] Peak booking times (heatmap)
- [ ] Revenue from bookings
- [ ] No-show rate
- [ ] Average lead time (how far in advance do people book?)
- [ ] Conversion rate: booking page views → completed bookings

### Agent Tools (Phase 5)
- [ ] `create_service` — Add a bookable service
- [ ] `set_availability` — Configure schedule
- [ ] `generate_booking_page` — Create/customize booking page
- [ ] `view_bookings` — Check upcoming schedule
- [ ] `reschedule_booking` — Move a booking
- [ ] `block_dates` — Mark dates unavailable

### Database Schema (Phase 5 additions)
```sql
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration INTEGER NOT NULL, -- minutes
    price DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    capacity INTEGER DEFAULT 1, -- 1 = individual, >1 = group
    category VARCHAR(100),
    color VARCHAR(7), -- hex color for calendar display
    intake_fields JSONB DEFAULT '[]', -- custom fields
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    settings JSONB DEFAULT '{}', -- buffer, notice, max_advance
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE availability_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id), -- null = applies to all
    name VARCHAR(255) DEFAULT 'Default',
    timezone VARCHAR(100) NOT NULL DEFAULT 'UTC',
    schedule JSONB NOT NULL, -- {mon: [{start: "09:00", end: "17:00"}], tue: [...], ...}
    buffer_minutes INTEGER DEFAULT 0,
    min_notice_hours INTEGER DEFAULT 1,
    max_advance_days INTEGER DEFAULT 60,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE blocked_dates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    start_time TIME, -- null = all day
    end_time TIME,
    reason VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE SET NULL,
    contact_id UUID REFERENCES contacts(id),
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    client_phone VARCHAR(50),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    status VARCHAR(50) DEFAULT 'confirmed', -- pending, confirmed, completed, cancelled, no_show
    intake_data JSONB DEFAULT '{}',
    notes TEXT,
    internal_notes TEXT,
    payment_amount DECIMAL(10,2) DEFAULT 0,
    payment_status VARCHAR(50), -- pending, paid, refunded
    payment_id VARCHAR(255), -- Stripe payment ID
    google_event_id VARCHAR(255), -- synced Google Calendar event
    cancellation_reason TEXT,
    cancelled_at TIMESTAMPTZ,
    reschedule_token VARCHAR(255) UNIQUE, -- for self-service reschedule
    cancel_token VARCHAR(255) UNIQUE, -- for self-service cancel
    series_id UUID, -- for recurring bookings
    reminder_sent BOOLEAN DEFAULT FALSE,
    followup_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE booking_series (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id),
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    recurrence_rule VARCHAR(100), -- weekly, biweekly, monthly
    total_sessions INTEGER,
    sessions_completed INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, cancelled
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 10,
    registered_count INTEGER DEFAULT 0,
    waitlist_enabled BOOLEAN DEFAULT TRUE,
    price DECIMAL(10,2) DEFAULT 0,
    location TEXT,
    is_online BOOLEAN DEFAULT FALSE,
    online_url TEXT,
    recurrence_rule VARCHAR(100),
    status VARCHAR(50) DEFAULT 'upcoming', -- upcoming, in_progress, completed, cancelled
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE event_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'registered', -- registered, waitlisted, cancelled, attended
    payment_status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(event_id, email)
);

CREATE TABLE google_calendar_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    google_account_email VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at TIMESTAMPTZ NOT NULL,
    calendar_ids TEXT[] DEFAULT '{}', -- which calendars to sync
    sync_channel_id VARCHAR(255), -- for push notifications
    sync_channel_expiry TIMESTAMPTZ,
    last_sync_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] User can create services with duration, price, capacity
- [ ] User can set availability schedules and blocked dates
- [ ] Public booking page shows available dates/times
- [ ] Client can book, receive confirmation email + .ics
- [ ] Payment at booking works (Stripe)
- [ ] Google Calendar 2-way sync works
- [ ] Reminders send at configured times
- [ ] Client can self-reschedule and self-cancel
- [ ] Group events/classes with capacity and waitlist work
- [ ] Recurring appointments can be created and managed
- [ ] Booking analytics dashboard shows key metrics
- [ ] Agent can manage services and availability via commands
- [ ] Booking page is mobile-friendly and embeddable

## Known Risks
- Google Calendar API quotas: 1M queries/day is generous but watch for push notification limits
- Timezone handling: Most common source of booking bugs. Use UTC everywhere internally.
- Slot calculation performance: Real-time availability checks must be fast. Cache aggressively.

## What's Next
Phase 6 (Payments) — required for monetizing bookings and courses.
