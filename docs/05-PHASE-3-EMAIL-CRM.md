# Phase 3 — Email / CRM

> **Goal**: Build the email marketing system, contact management, automation workflows, and SES integration with custom domain sending. After this phase, users can build email lists, send campaigns, and run automated sequences.

## Status: NOT STARTED

## Dependencies
- Phase 0 (Foundation) — auth, DB
- Phase 2 (Dashboard) — UI shell, notification system

## Checklist

### Contact Management
- [ ] Contact data model: email, name, phone, tags, custom fields, source, score
- [ ] Contact list view: search, filter by tags/segments, sort
- [ ] Contact detail view: profile, activity timeline, tags, notes
- [ ] Contact import: CSV upload with field mapping, deduplication
- [ ] Contact export: CSV download
- [ ] Manual contact add/edit
- [ ] Bulk actions: tag, untag, delete, add to sequence
- [ ] Contact merge (duplicates)
- [ ] Unsubscribe handling: automatic removal, compliance log

### Segments
- [ ] Static segments: manually add contacts
- [ ] Dynamic segments: rule-based (tag = X, opened email Y, purchased Z, etc.)
- [ ] Segment builder UI: visual condition builder (AND/OR logic)
- [ ] Pre-built segments: "All contacts", "Engaged (last 30 days)", "Inactive", "Customers"

### Email Builder
- [ ] Block-based drag-drop editor:
  - [ ] Text block (rich text)
  - [ ] Image block (upload or media library)
  - [ ] Button block (CTA with URL)
  - [ ] Divider block
  - [ ] Column layout (2-col, 3-col)
  - [ ] Social links block
  - [ ] Unsubscribe footer (auto-added, required)
- [ ] Template library: pre-designed email templates (welcome, newsletter, promo, announcement)
- [ ] Merge tags: {{first_name}}, {{company}}, {{custom_field}}, etc.
- [ ] Mobile preview
- [ ] HTML source editor (advanced)
- [ ] Test send (send to self before campaign)
- [ ] Agent-generated emails ("Write a welcome email for new yoga students")

### Campaigns
- [ ] Campaign creation: select segment, choose/build email, set subject + preview text
- [ ] Send options: send now, schedule for later, timezone-optimized sending
- [ ] A/B testing: subject line variants (2-way split, auto-choose winner)
- [ ] Campaign analytics: sent, delivered, opened, clicked, bounced, unsubscribed
- [ ] Click map: which links got clicked
- [ ] Campaign list with status (draft, scheduled, sent, sending)

### Automation Sequences
- [ ] Visual automation builder (flow diagram):
  - [ ] Triggers: form submission, tag added, purchase, manual enrollment, date-based
  - [ ] Actions: send email, wait (delay), add tag, remove tag, notify owner, update contact field
  - [ ] Conditions: if opened email, if clicked link, if has tag, if score > X
  - [ ] Branch logic: if/else splits
- [ ] Pre-built automations: Welcome sequence, Abandoned cart, Re-engagement, Post-purchase
- [ ] Automation analytics: enrolled, completed, dropped off, conversion rate
- [ ] Pause/resume automations

### Lead Scoring
- [ ] Point system: +10 for email open, +20 for click, +50 for purchase, -10 for inactivity
- [ ] Configurable scoring rules
- [ ] Score displayed on contact profile
- [ ] Segment by score range

### Deal Pipeline (Lightweight CRM)
- [ ] Kanban board: Lead → Contacted → Proposal → Negotiation → Won / Lost
- [ ] Drag contacts between stages
- [ ] Deal value, expected close date, notes
- [ ] Pipeline analytics: conversion rate per stage, average deal time

### AWS SES Integration
- [ ] SES domain verification (DKIM + SPF + DMARC)
- [ ] Custom "from" address: notifications@userdomain.com
- [ ] Sending rate management (honor SES limits)
- [ ] Bounce + complaint handling (auto-unsubscribe hard bounces)
- [ ] Deliverability dashboard: reputation score, bounce rate, complaint rate
- [ ] Warmup guidance: gradual volume increase for new domains
- [ ] Suppression list management

### Agent Tools (Phase 3)
- [ ] `create_email_sequence` — Build automation from description
- [ ] `send_campaign` — Create and schedule email campaign
- [ ] `write_email` — Generate email copy for any purpose
- [ ] `add_contacts` — Import or add contacts
- [ ] `create_segment` — Build segment from description
- [ ] `check_deliverability` — Report on email health

### Database Schema (Phase 3 additions)
```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(50),
    source VARCHAR(100), -- form, import, manual, api
    tags TEXT[] DEFAULT '{}',
    custom_fields JSONB DEFAULT '{}',
    lead_score INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- active, unsubscribed, bounced, complained
    unsubscribed_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(org_id, email)
);

CREATE TABLE segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) DEFAULT 'dynamic', -- static, dynamic
    rules JSONB, -- for dynamic: condition tree
    contact_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE segment_contacts (
    segment_id UUID REFERENCES segments(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    PRIMARY KEY (segment_id, contact_id)
);

CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id), -- null = system template
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    preview_text VARCHAR(255),
    blocks JSONB NOT NULL DEFAULT '[]',
    html_content TEXT, -- compiled HTML
    category VARCHAR(100), -- welcome, newsletter, promo, transactional
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    preview_text VARCHAR(255),
    template_id UUID REFERENCES email_templates(id),
    segment_id UUID REFERENCES segments(id),
    from_name VARCHAR(255),
    from_email VARCHAR(255),
    reply_to VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft', -- draft, scheduled, sending, sent, cancelled
    scheduled_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    stats JSONB DEFAULT '{"sent":0,"delivered":0,"opened":0,"clicked":0,"bounced":0,"unsubscribed":0}',
    ab_test JSONB, -- {variant_b_subject, split_pct, winner_metric}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE campaign_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- sent, delivered, opened, clicked, bounced, unsubscribed, complained
    link_url TEXT, -- for click events
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE automations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    trigger_type VARCHAR(100) NOT NULL, -- form_submit, tag_added, purchase, manual, date
    trigger_config JSONB DEFAULT '{}',
    steps JSONB NOT NULL DEFAULT '[]', -- ordered steps: {type, config, delay}
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, paused
    enrolled_count INTEGER DEFAULT 0,
    completed_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE automation_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    automation_id UUID REFERENCES automations(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    current_step INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, paused, exited
    next_action_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    title VARCHAR(255) NOT NULL,
    value DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'USD',
    stage VARCHAR(100) DEFAULT 'lead', -- lead, contacted, proposal, negotiation, won, lost
    expected_close_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE scoring_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL, -- email_open, email_click, form_submit, purchase, inactivity
    points INTEGER NOT NULL, -- can be negative
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] User can add/import contacts (CSV with mapping)
- [ ] User can create dynamic segments with conditions
- [ ] User can build emails with drag-drop editor
- [ ] User can send campaigns (now or scheduled) to segments
- [ ] Campaign analytics show opens, clicks, bounces
- [ ] User can build automation sequences (visual flow builder)
- [ ] Automations trigger and execute correctly (send email → wait → check condition → etc.)
- [ ] SES sends emails from user's verified custom domain
- [ ] Bounce/complaint handling auto-updates contact status
- [ ] Lead scoring updates on engagement events
- [ ] Deal pipeline shows kanban board with drag-drop
- [ ] Agent can create sequences and campaigns via commands
- [ ] All email has unsubscribe link and compliance footer

## Known Risks
- SES sandbox: New SES accounts start in sandbox (can only send to verified emails). Need to request production access.
- Custom domain verification: DNS changes take time. Need good UX for guiding users through DKIM/SPF setup.
- Email deliverability: New domains have no reputation. Warmup is critical.
- Automation engine: Reliable delayed execution (wait X days) requires a robust job queue (Celery + Redis).

## What's Next
Phase 4 (Courses & Memberships) or Phase 5 (Calendar) — can be parallel.
