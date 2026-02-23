# Phase 9 — Admin Panel

> **Goal**: Build the platform administration dashboard for managing users, revenue, system health, content moderation, and feature flags. After this phase, we have full operational control.

## Status: NOT STARTED

## Dependencies
- All previous phases (aggregates data from all features)

## Checklist

### User Management
- [ ] User list: search, filter by plan/status/created date, sort
- [ ] User detail: account info, org, plan, usage, activity, payments
- [ ] User lifecycle management:
  - [ ] Activate/deactivate account
  - [ ] Suspend (temporary, with reason)
  - [ ] Delete (with data cleanup, GDPR compliance)
  - [ ] Change plan manually (override billing)
- [ ] Impersonation: "View as user" without affecting their data (read-only mode)
- [ ] Send notification to user (system message)
- [ ] Bulk actions: email blast to all users, export user list
- [ ] User activity log: recent actions, last login, pages created, emails sent

### Revenue & Business Analytics
- [ ] Platform MRR: total, by plan tier
- [ ] Churn rate: monthly, by cohort
- [ ] LTV (Lifetime Value) calculation
- [ ] ARPU (Average Revenue Per User)
- [ ] New signups: daily/weekly/monthly, conversion from trial
- [ ] Revenue by source: subscriptions, platform fees
- [ ] Transaction fees collected
- [ ] Payout summary
- [ ] Charts: MRR growth, churn trend, signup funnel
- [ ] Export: CSV/PDF reports

### Feature Flags
- [ ] Flag management: create, enable/disable, set target (all, % rollout, specific users/plans)
- [ ] Flag types: boolean, string, number
- [ ] Usage in code: simple API check `is_feature_enabled("new_editor", org_id)`
- [ ] Flag history: who changed what, when

### System Health Dashboard
- [ ] Service status: API, Database, Redis, S3, SES, LLM APIs, CloudFront
- [ ] Uptime monitoring: green/yellow/red indicators
- [ ] Error rate tracking: 5xx errors, 4xx spikes
- [ ] API response time: p50, p95, p99
- [ ] Queue health: Celery task queue depth, processing rate
- [ ] Storage usage: total S3 storage, by user breakdown
- [ ] Email health: SES sending rate, bounce rate, complaint rate
- [ ] Agent usage: total tokens consumed, by model, by user
- [ ] Database metrics: connection count, query performance
- [ ] Alerts: configurable thresholds → email/Slack notification

### Content Moderation
- [ ] Automated scanning: flag content with harmful/spam patterns
- [ ] Moderation queue: review flagged content (pages, community posts, emails)
- [ ] Actions: approve, remove, warn user, suspend user
- [ ] Report handling: user-submitted reports
- [ ] Moderation log: all actions with moderator and timestamp

### Audit Log
- [ ] All admin actions logged: user changes, feature flags, moderation
- [ ] Filterable by admin, action type, date range
- [ ] Immutable (append-only)
- [ ] Retention: 1 year minimum

### Template Management
- [ ] Template CRUD: create, edit, preview, activate/deactivate
- [ ] Template analytics: usage count, user ratings, conversion data
- [ ] Component CRUD: manage reusable UI components
- [ ] Template categories management

### Support System (Basic)
- [ ] Ticket list: open, in-progress, resolved
- [ ] Ticket detail: user info, conversation thread, attachments
- [ ] Assign to admin
- [ ] Priority levels: low, medium, high, urgent
- [ ] Auto-response for common questions (FAQ-based)
- [ ] User-facing: "Contact Support" form in dashboard

### Database Schema (Phase 9 additions)
```sql
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    flag_type VARCHAR(20) DEFAULT 'boolean', -- boolean, string, number
    default_value JSONB NOT NULL DEFAULT 'false',
    is_enabled BOOLEAN DEFAULT FALSE,
    target_type VARCHAR(50) DEFAULT 'all', -- all, percentage, users, plans
    target_config JSONB DEFAULT '{}', -- {percentage: 10} or {user_ids: [...]} or {plans: ["pro"]}
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE feature_flag_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_id UUID REFERENCES feature_flags(id) ON DELETE CASCADE,
    changed_by UUID REFERENCES users(id),
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE admin_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(100),
    target_id UUID,
    details JSONB DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id),
    subject VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, resolved, closed
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    category VARCHAR(100),
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE TABLE support_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id),
    is_admin BOOLEAN DEFAULT FALSE,
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE content_moderation_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type VARCHAR(50) NOT NULL, -- page, post, email
    content_id UUID NOT NULL,
    org_id UUID REFERENCES organizations(id),
    reason VARCHAR(255), -- auto-detected reason or user report
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, removed, warned
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE system_health_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service VARCHAR(100) NOT NULL, -- api, database, redis, s3, ses, llm, cloudfront
    status VARCHAR(20) NOT NULL, -- healthy, degraded, down
    response_time_ms INTEGER,
    details JSONB DEFAULT '{}',
    checked_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] Admin can view and manage all users
- [ ] Admin can impersonate users (read-only view-as)
- [ ] Revenue dashboard shows MRR, churn, LTV, ARPU
- [ ] Feature flags can be created, toggled, and targeted
- [ ] System health dashboard shows all service statuses
- [ ] Content moderation queue shows flagged content
- [ ] Audit log records all admin actions
- [ ] Support ticket system allows user-admin communication
- [ ] Template management CRUD works

## Known Risks
- Admin panel security: Must be strictly access-controlled (is_admin flag + separate URL path)
- Impersonation: Must log all impersonation sessions and ensure no write actions
- Audit log size: Can grow large. Implement archival/rotation strategy.

## What's Next
Phase 10 (Polish & Launch Prep).
