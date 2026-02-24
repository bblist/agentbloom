# AgentBloom — Developer Handoff Document

> **Last updated:** Phase 5 completion  
> **Git HEAD:** (to be set after commit)  
> **Author:** AI Dev (Phases 1–5)

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
| DevOps | Docker Compose (6 services), GitHub Actions (CI placeholder) |

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

## 7. What Remains (Priority Order)

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

5. **Stripe Connect onboarding flow**  
   `payments/views.py` — `StripeConnectionViewSet.onboard()` and `.status()` are still TODO stubs. Need Stripe Connect OAuth redirect + webhook verification.

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

11. **Frontend error handling / loading states**  
    Most pages have basic try/catch but could benefit from React Error Boundaries, skeleton loaders, and toast notifications.

12. **RBAC / permissions**  
    Currently most views use `IsAuthenticated`. Need per-org role checks (admin, editor, viewer) on destructive actions.

### 🟢 Nice to Have

13. **Tests** — Zero test files exist. Recommend: pytest-django + factory_boy for backend, Vitest + RTL for frontend.

14. **CI/CD pipeline** — GitHub Actions workflow file exists but is a placeholder. Wire up: lint → test → build → deploy.

15. **Rate limiting** — DRF throttle classes are configured but may need per-endpoint tuning.

16. **WebSocket reconnection** — Agent chat SSE/WS should gracefully reconnect on network drops.

17. **Internationalization** — i18n is enabled in Django but no translations exist.

18. **Monitoring / APM** — Consider Sentry, Datadog, or AWS CloudWatch.

---

## 8. Key Files Quick Reference

| File | Purpose |
|------|---------|
| `backend/agentbloom/settings.py` | All Django settings — AWS, Stripe, LLM keys, Celery, etc. |
| `backend/agentbloom/urls.py` | Main URL dispatcher — all 13 apps mounted at `/api/v1/` |
| `backend/apps/agent/engine.py` | ReAct agent loop — tool selection, LLM calls, streaming |
| `backend/apps/agent/tools/` | 15 agent tools (site builder, CRM, email, etc.) |
| `backend/apps/sites/renderer.py` | HTML page renderer — 18 block types → HTML |
| `frontend/src/lib/api.ts` | Axios client — all API methods, auth interceptor |
| `frontend/src/lib/store.ts` | Zustand auth store — login, logout, hydrate |
| `frontend/src/middleware.ts` | Next.js auth middleware — route protection |
| `frontend/src/app/dashboard/layout.tsx` | Dashboard shell — sidebar nav, org context |
| `docker-compose.yml` | 6 services: db, redis, backend, celery, celery-beat, frontend |
| `backend/Dockerfile` | Multi-stage build, daphne ASGI server |
| `frontend/Dockerfile` | Multi-stage build, standalone Next.js output |

---

## 9. Docker Quick Start

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

## 10. Deployment Checklist (Lightsail)

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
