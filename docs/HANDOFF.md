# AgentBloom — Developer Handoff Document

> **Last updated:** Phase 6 completion  
> **Git HEAD:** (to be set after commit)  
> **Author:** AI Dev (Phases 1–6)

---

## 1. Project Overview

**AgentBloom** is a multi-tenant SaaS platform that enables local businesses to deploy AI-powered agents for website building, CRM, email campaigns, course hosting, appointment booking, SEO, payment processing, and admin management — all unified under a single dashboard.

| Layer | Stack |
|-------|-------|
| Backend | Django 5.1, DRF, Channels (ASGI/WebSocket), Celery + django-celery-beat |
| Frontend | Next.js 15.1, React 19, Tailwind v4, Zustand, TanStack React Query, Recharts |
| Database | PostgreSQL 16 + pgvector, Redis 7 |
| LLM | OpenAI (GPT-4o primary), Anthropic (Claude, design default), Google (Gemini) |
| Infra | AWS Lightsail, SES, S3 + CloudFront, Route 53 |
| DevOps | Docker Compose (6 services), GitHub Actions CI/CD (lint → test → build → deploy) |

**Repo:** `github.com/bblist/agentbloom`  
**DNS:** `agentbloom.nobleblocks.com` → `52.1.31.54` (Lightsail)  
**Route 53 Zone:** `Z09431023T50KZYMBGV70`

---

## 2. Git History / Phase Summary

| Commit | Phase | Summary |
|--------|-------|---------|
| `518c168` | Pre-1 | LLM strategy update — Claude as design default |
| `b067200` | **Phase 1** | Agent engine (ReAct loop), 15 tools, ChatView + WebSocket, Page Renderer (18 block types), frontend dashboard + agent chat + settings, 5 template fixtures |
| `11ccfdd` | **Phase 2** | Serializers/views/URLs for all 12 apps, Celery tasks for all apps, Beat schedule, task integrations |
| `0192b91` | **Phase 3** | All 5 placeholder frontend pages → full implementations, dashboard live stats, API client (60+ methods), management commands |
| `25187ba` | **DiceBear** | All emoji icons → DiceBear API avatar components across 13 pages |
| `717db07` | **Phase 4** | Auth endpoints (login/logout/token), Docker fixes, 4 new pages (KB, Admin, Notifications, Webhooks), API client fixes, Recharts, Stripe dep added |
| *(pending)* | **Phase 5** | URL alignment, missing views, SES wiring, S3 storage, Stripe config, auth middleware, Zustand store, migration dirs |
| *(pending)* | **Phase 6** | Stripe Connect wired, all TODO stubs resolved, RBAC permissions, test infrastructure (pytest + factories), CI/CD pipeline (pytest), frontend UX (ErrorBoundary, Skeleton, AuthProvider), .env.example |

---

## 3. Architecture

```
┌─────────────────────────────────────────────────┐
│                  Frontend (Next.js 15)          │
│  /app/page.tsx              — Landing           │
│  /app/auth/login,register   — Auth              │
│  /app/dashboard/*           — 13 dashboard pages│
│  /lib/api.ts                — Axios API client  │
│  /lib/store.ts              — Zustand auth store│
│  /middleware.ts             — Auth route guard   │
└─────────────────┬───────────────────────────────┘
                  │ REST / SSE / WebSocket
┌─────────────────▼───────────────────────────────┐
│               Backend (Django 5.1 / Daphne)     │
│  /api/v1/auth/        — Login, logout, token    │
│  /api/v1/orgs/        — Multi-tenant orgs       │
│  /api/v1/agent/       — Chat, conversations     │
│  /api/v1/sites/       — Site builder            │
│  /api/v1/crm/         — CRM + email campaigns   │
│  /api/v1/courses/     — LMS                     │
│  /api/v1/calendar/    — Bookings + scheduling   │
│  /api/v1/kb/          — Knowledge base          │
│  /api/v1/seo/         — SEO tools               │
│  /api/v1/payments/    — Stripe + invoicing      │
│  /api/v1/admin-panel/ — Admin tools             │
│  /api/v1/notifications/— Alerts + preferences   │
│  /api/v1/webhooks/    — Webhook management      │
│  /ws/agent/chat/      — WebSocket agent chat    │
└──────┬──────────┬───────────────────────────────┘
       │          │
  ┌────▼────┐ ┌───▼────┐
  │ Celery  │ │ Redis  │
  │ + Beat  │ │  Cache │
  └────┬────┘ └────────┘
       │
  ┌────▼────────────────┐
  │ PostgreSQL 16       │
  │ + pgvector          │
  └─────────────────────┘
```

---

## 4. Backend Apps (13 total)

| App | Models (approx) | Key Endpoints |
|-----|-----------------|---------------|
| `users` | User (custom), Profile | Auth, profile |
| `orgs` | Organization, Membership, Invite | CRUD, invites |
| `agent` | Conversation, Message, LLMProviderConfig, Template | Chat (SSE+WS), tools |
| `sites` | Site, Page, ContentBlock, Form, FormSubmission, SEOSettings | Full CRUD, publish to CDN |
| `email_crm` | Contact, Segment, Campaign, CampaignEvent, Template, ScoringRule, Pipeline, Deal | Campaign send, scoring, CSV import |
| `courses` | Course, Section, Lesson, Enrollment, LessonProgress, CourseAnnouncement, Certificate | Progress tracking, certificates |
| `calendar_booking` | Service, AvailabilitySchedule, Booking, BookingAnalytics, GoogleCalendarConnection | Booking CRUD, reminders |
| `kb` | KBDocument, DocumentChunk, ScrapeSchedule, KBCollection | Upload, scrape, vectorize |
| `seo` | SEOAudit, AuditIssue, KeywordRank, BacklinkProfile, PageSpeedResult | Audit, keyword track |
| `payments` | StripeConnection, Subscription, Plan, Invoice, Payment, Refund, RevenueSnapshot, Coupon | Stripe onboard, webhooks, revenue |
| `admin_panel` | FeatureFlag, AdminAuditLog, SupportTicket, SupportMessage, ContentModerationQueue, SystemHealthCheck, ImpersonationSession, UserLifecycleEvent, RevenueAnalytics, PlatformMetrics | Admin CRUD, health checks, user management |
| `notifications` | Notification, NotificationPreference, ActivityFeedEntry | In-app + email, preferences singleton |
| `webhooks` | WebhookEndpoint, WebhookEvent, WebhookDeliveryLog, IncomingWebhook | CRUD, test, delivery logs |

---

## 5. Frontend Pages (17 total)

| Path | Description |
|------|-------------|
| `/` | Landing page |
| `/auth/login` | Login (wired to `authAPI`) |
| `/auth/register` | Registration |
| `/dashboard` | Main dashboard — live stats, quick actions |
| `/dashboard/agent` | Agent chat with SSE streaming |
| `/dashboard/sites` | Site builder management |
| `/dashboard/crm` | CRM contacts + campaigns |
| `/dashboard/courses` | Course/LMS management |
| `/dashboard/bookings` | Appointment booking |
| `/dashboard/payments` | Stripe + invoices + revenue |
| `/dashboard/seo` | SEO audits + keywords |
| `/dashboard/kb` | Knowledge base documents |
| `/dashboard/settings` | Org settings + LLM config |
| `/dashboard/admin` | Admin panel (users, tickets, health) |
| `/dashboard/notifications` | Notifications + preferences |
| `/dashboard/webhooks` | Webhook endpoints + logs |

All pages use DiceBear API avatars (no emojis).

---

## 6. What Phase 5 Accomplished

### 6.1 Backend URL Alignment
All frontend API paths now match backend router registrations:

| File | Before → After |
|------|----------------|
| `admin_panel/urls.py` | `support-tickets` → `tickets`, `health` → `system-health`, `audit-logs` → `audit-log`, `revenue-analytics` → `revenue`, **added** `users` route |
| `notifications/urls.py` | **Complete rewrite** — router → manual URL patterns to eliminate double-nesting (`/notifications/notifications/` → `/notifications/`) |
| `webhooks/urls.py` | `webhook-endpoints` → `endpoints`, `webhook-events` → `events`, `webhook-logs` → `logs` |
| `payments/urls.py` | `stripe` → `stripe-connection`, `revenue` → `revenue-snapshots` |
| `calendar_booking/urls.py` | `availability` → `schedules` |
| `kb/urls.py` | `scrape-schedules` → `sources` |

### 6.2 Missing Backend Views Added
- **`AdminUserViewSet`** (`admin_panel/views.py`) — ReadOnlyModelViewSet for listing platform users with `impersonate` action
- **`NotificationPreferenceSingletonView`** (`notifications/views.py`) — APIView (GET/PATCH) for current user's notification preferences (auto-creates if missing)
- **`deliveries` action** (`webhooks/views.py`) — GET action on `WebhookEndpointViewSet` returning paginated delivery logs for a specific endpoint

### 6.3 SES Email Wiring
Replaced all `# TODO: Send via SES` stubs across 6 task files with actual `django.core.mail.send_mail()` calls:
- `calendar_booking/tasks.py` — booking confirmation + reminders
- `courses/tasks.py` — course announcements
- `email_crm/tasks.py` — campaign emails
- `notifications/tasks.py` — notification emails (with preference check)
- `payments/tasks.py` — payment receipts + dunning emails
- `sites/tasks.py` — form submission notifications + CRM contact creation

### 6.4 S3 + CloudFront Wiring
- `settings.py` — `STORAGES["default"]` now uses `S3Boto3Storage` in production, `FileSystemStorage` in dev
- `settings.py` — Added `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`, `AWS_S3_FILE_OVERWRITE`, `AWS_DEFAULT_ACL`, `AWS_S3_CUSTOM_DOMAIN`
- `sites/tasks.py` — `publish_site_to_cdn()` now uploads rendered HTML to S3
- `sites/tasks.py` — `invalidate_cdn_cache()` now calls CloudFront invalidation API

### 6.5 Stripe Config
- `settings.py` — Added `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` env vars

### 6.6 Auth Middleware + State
- **`frontend/src/middleware.ts`** — Next.js Edge Middleware protecting `/dashboard/*` routes; redirects to `/auth/login` if no `auth_token` cookie
- **`frontend/src/lib/store.ts`** — Zustand-powered auth store with `login()`, `logout()`, `hydrate()`, `setOrg()` actions; persisted to localStorage

### 6.7 Migration Directories
- Created `migrations/__init__.py` for all 13 apps (migrations must be generated inside Docker)

---

## 7. What Phase 6 Accomplished

### 7.1 All Remaining TODO Stubs Resolved
Every `# TODO` stub across the codebase was replaced with working implementations (11 replacements across 7 files).

### 7.2 Stripe Connect Onboarding (Full Flow)
- `payments/views.py` — `StripeConnectionViewSet.onboard()` now creates a Stripe Express account via `stripe.Account.create()`, generates an `AccountLink` for onboarding redirect, and returns the URL to the frontend.
- `RefundViewSet.approve()` now calls `stripe.Refund.create()` with charge ID and amount.
- `InvoiceViewSet.send_invoice()` now sends invoice emails via `send_mail()`.

### 7.3 S3 File Uploads Wired
- `kb/views.py` — File upload uses `default_storage.save()` (S3 in prod), triggers `process_kb_document.delay()` for async vectorization. Scrape action triggers `scrape_url.delay()`.
- `seo/views.py` — `generate_sitemap()` builds XML sitemap from published pages, uploads to S3.
- `sites/views.py` — `MediaLibraryViewSet.perform_create()` saves uploaded files via `default_storage`.

### 7.4 Webhook Routing
- `webhooks/tasks.py` — `process_incoming_webhook()` now dispatches: `stripe` → `process_stripe_webhook.delay()`, `google` → `sync_google_calendar.delay()`, `ses` → `process_email_event.delay()`.

### 7.5 Admin Moderation Alerts
- `admin_panel/tasks.py` — `check_content_moderation_queue()` creates `Notification` objects for all staff users when the moderation queue exceeds 50 items.

### 7.6 Frontend UX Components
- **`ErrorBoundary`** (`components/error-boundary.tsx`) — React class component with styled fallback UI, error message display, and "Try Again" button.
- **`Skeleton` / `PageSkeleton` / `CardSkeleton`** (`components/skeleton.tsx`) — Animated loading placeholders for pages, cards, and tables.
- **`AuthProvider`** (`components/auth-provider.tsx`) — Client component that hydrates the Zustand auth store on mount.
- **`layout.tsx`** — Root layout now wraps children with `AuthProvider` + `ErrorBoundary`.
- **Dashboard layout** — Upgraded with auth store integration: user avatar, name/email display, org selector, logout button with toast.

### 7.7 RBAC Permission Classes
- `users/permissions.py` — Four DRF permission classes:
  - `IsOrgMember` — any org member (staff bypass)
  - `IsOrgAdmin` — owner or admin role (staff bypass)
  - `IsOrgOwner` — owner only (superuser bypass)
  - `ReadOnlyForMembers` — safe methods for members, full CRUD for admin/owner
- `users/middleware.py` — Enhanced to also attach `request.org_role` from membership lookup.

### 7.8 Test Infrastructure
- `pytest.ini` — Configured with `DJANGO_SETTINGS_MODULE`, markers for `slow`/`integration`.
- `conftest.py` — Three factories (`UserFactory`, `OrganizationFactory`, `OrgMemberFactory`) + 7 fixtures (`user`, `admin_user`, `org`, `member_user`, `api_client`, `auth_client`, `admin_client`).
- `users/tests/test_auth.py` — 5 tests for login/logout endpoints.
- `users/tests/test_permissions.py` — 7 tests for RBAC permission classes.
- `agent/tests/test_agent.py` — 3 tests for conversation CRUD and chat.

### 7.9 CI/CD Pipeline
- `.github/workflows/ci.yml` — Updated to use `pytest --cov=apps` instead of `manage.py test`. Three jobs: backend (postgres+redis services, ruff lint, pytest), frontend (lint+typecheck+build), deploy (SSH to Lightsail, docker compose up).

### 7.10 Developer Onboarding
- `.env.example` created at project root with all required environment variables, organized by category.

---

## 8. What Remains (Priority Order)

### 🔴 Critical — Must Do Before Deploy

1. **Generate Django migrations**  
   Run inside Docker: `docker compose exec backend python manage.py makemigrations && docker compose exec backend python manage.py migrate`  
   All 13 apps have models but zero migration files.

2. **Create superuser**  
   `docker compose exec backend python manage.py createsuperuser`

3. **SSL/TLS certificate**  
   Set up Let's Encrypt / Certbot on Lightsail for `agentbloom.nobleblocks.com`. Nginx reverse proxy config needed.

4. **Environment variables on Lightsail**  
   Production `.env` file needs all secrets:
   ```
   DJANGO_SECRET_KEY=<generate>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=agentbloom.nobleblocks.com
   DATABASE_URL=postgres://...
   REDIS_URL=redis://redis:6379/0
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   STRIPE_SECRET_KEY=...
   STRIPE_PUBLISHABLE_KEY=...
   STRIPE_WEBHOOK_SECRET=...
   OPENAI_API_KEY=...
   ANTHROPIC_API_KEY=...
   ```

### 🟡 Important — Should Do Before Beta

5. ~~**Stripe Connect onboarding flow**~~ ✅ Done in Phase 6

6. **Stripe subscription sync**  
   `payments/tasks.py` — `sync_stripe_subscriptions()` is a stub. Needs `stripe.Subscription.list()` integration.

7. **Google Calendar sync**  
   `calendar_booking/tasks.py` — `sync_google_calendar()` is a stub. Needs Google Calendar API OAuth + event sync.

8. **SEO API integrations**  
   - `seo/tasks.py` — `track_keyword_rankings()` needs a SERP API (e.g., SerpApi, DataForSEO)
   - `seo/tasks.py` — `check_page_speeds()` needs Google PageSpeed Insights API

9. **Site preview generation**  
   `sites/tasks.py` — `generate_site_preview()` needs Playwright or Puppeteer for screenshots.

10. **Certificate PDF generation**  
    `courses/tasks.py` — `generate_certificate()` creates DB record but doesn't generate actual PDF. Needs reportlab/weasyprint + S3 upload.

11. ~~**Frontend error handling / loading states**~~ ✅ Done in Phase 6 (ErrorBoundary, Skeleton, AuthProvider)

12. ~~**RBAC / permissions**~~ ✅ Done in Phase 6 (IsOrgMember, IsOrgAdmin, IsOrgOwner, ReadOnlyForMembers)

### 🟢 Nice to Have

13. **Tests** — 15 tests exist (auth, permissions, agent). Expand to cover all apps. Recommend Vitest + RTL for frontend.

14. ~~**CI/CD pipeline**~~ ✅ Done in Phase 6 (pytest, ruff, deploy to Lightsail)

15. **Rate limiting** — DRF throttle classes are configured but may need per-endpoint tuning.

16. **WebSocket reconnection** — Agent chat SSE/WS should gracefully reconnect on network drops.

17. **Internationalization** — i18n is enabled in Django but no translations exist.

18. **Monitoring / APM** — Consider Sentry, Datadog, or AWS CloudWatch.

---

## 9. Key Files Quick Reference

| File | Purpose |
|------|---------|
| `backend/agentbloom/settings.py` | All Django settings — AWS, Stripe, LLM keys, Celery, etc. |
| `backend/agentbloom/urls.py` | Main URL dispatcher — all 13 apps mounted at `/api/v1/` |
| `backend/apps/agent/engine.py` | ReAct agent loop — tool selection, LLM calls, streaming |
| `backend/apps/agent/tools/` | 15 agent tools (site builder, CRM, email, etc.) |
| `backend/apps/sites/renderer.py` | HTML page renderer — 18 block types → HTML |
| `backend/apps/users/permissions.py` | RBAC permission classes — IsOrgMember, IsOrgAdmin, IsOrgOwner |
| `backend/apps/users/middleware.py` | Org middleware — attaches request.org + request.org_role |
| `backend/conftest.py` | Test fixtures — factories, auth clients, org membership |
| `backend/pytest.ini` | Pytest config — DJANGO_SETTINGS_MODULE, markers |
| `frontend/src/lib/api.ts` | Axios client — all API methods, auth interceptor |
| `frontend/src/lib/store.ts` | Zustand auth store — login, logout, hydrate |
| `frontend/src/middleware.ts` | Next.js auth middleware — route protection |
| `frontend/src/components/error-boundary.tsx` | React ErrorBoundary with styled fallback |
| `frontend/src/components/skeleton.tsx` | Loading skeletons — PageSkeleton, CardSkeleton |
| `frontend/src/components/auth-provider.tsx` | Auth hydration on app mount |
| `frontend/src/app/dashboard/layout.tsx` | Dashboard shell — sidebar nav, org context, user info |
| `docker-compose.yml` | 6 services: db, redis, backend, celery, celery-beat, frontend |
| `.github/workflows/ci.yml` | CI/CD — ruff lint, pytest, frontend build, Lightsail deploy |
| `.env.example` | Template for all required environment variables |
| `backend/Dockerfile` | Multi-stage build, daphne ASGI server |
| `frontend/Dockerfile` | Multi-stage build, standalone Next.js output |

---

## 10. Docker Quick Start

```bash
# Clone
git clone https://github.com/bblist/agentbloom.git
cd agentbloom

# Create .env with required vars (see section 7.4 above)
cp .env.example .env  # then edit

# Build and start
docker compose up --build -d

# Generate migrations + migrate
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Load template fixtures
docker compose exec backend python manage.py loaddata fixtures/templates.json

# Frontend available at http://localhost:3000
# Backend API at http://localhost:8000/api/v1/
```

---

## 11. Deployment Checklist (Lightsail)

- [ ] SSH into `52.1.31.54`
- [ ] Clone repo / pull latest
- [ ] Create production `.env` file
- [ ] `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d`
- [ ] Run migrations + createsuperuser
- [ ] Set up Nginx reverse proxy with SSL (certbot)
- [ ] Verify DNS resolves `agentbloom.nobleblocks.com`
- [ ] Configure Stripe webhook endpoint in Stripe Dashboard → `https://agentbloom.nobleblocks.com/api/v1/webhooks/incoming/stripe/`
- [ ] Verify SES sending domain in AWS console
- [ ] Create S3 buckets: `agentbloom-assets`, `agentbloom-sites`
- [ ] Set up CloudFront distribution pointing to `agentbloom-sites` bucket

---

*End of handoff document.*
