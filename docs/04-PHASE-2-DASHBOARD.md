# Phase 2 — Dashboard + Visual Editor

> **Goal**: Build the full dashboard UI with all navigation, manual page editing, media library, and the visual block editor. After this phase, users can both talk to the agent AND manually edit their pages.

## Status: NOT STARTED

## Dependencies
- Phase 0 (Foundation) — auth, deployment
- Phase 1 (Agent + Pages) — agent chat, page data model

## Checklist

### Dashboard Shell
- [ ] Sidebar navigation with grouped sections:
  - **Build**: Site Builder, Pages, Templates, Media Library
  - **Engage**: (placeholder for Email, Calendar — Phase 3/5)
  - **Learn**: (placeholder for Courses — Phase 4)
  - **Money**: (placeholder for Payments, Analytics — Phase 6)
  - **Settings**: Domain, Account, Billing, Integrations
- [ ] Top bar: organization selector, notifications bell, user avatar menu
- [ ] Dashboard home: activity feed, setup progress, quick actions, site status
- [ ] Command palette (Cmd+K): search pages, templates, navigate sections, agent commands
- [ ] Responsive sidebar (collapsible on mobile, overlay drawer)
- [ ] Breadcrumb navigation
- [ ] Toast notifications (success, error, info)
- [ ] Loading skeletons for all data-loading states

### Visual Page Editor
- [ ] Split view: editor panel (left) + live preview (right)
- [ ] Block list: add, reorder (drag-drop), delete blocks
- [ ] Block types with visual editors:
  - [ ] Hero: headline, subheadline, background image/color, CTA button
  - [ ] Text: rich text editor (bold, italic, links, lists, headings)
  - [ ] Image: upload/select from media library, alt text, sizing
  - [ ] CTA: button text, URL, style (primary/secondary/outline)
  - [ ] Form: field configuration, submit action, styling
  - [ ] Pricing: tiers (name, price, features, CTA per tier)
  - [ ] Testimonials: name, photo, quote, rating, company
  - [ ] FAQ: expandable Q&A pairs
  - [ ] Gallery: grid/carousel of images
  - [ ] Video: YouTube/Vimeo embed or uploaded video
  - [ ] Footer: links, social icons, copyright
  - [ ] Spacer/Divider: spacing control
  - [ ] Custom HTML: code editor for advanced users
- [ ] Global styles panel: colors (primary, secondary, accent, background, text), fonts, border radius
- [ ] Per-block style overrides: padding, margin, background, border
- [ ] Undo/redo (Ctrl+Z / Ctrl+Shift+Z)
- [ ] Auto-save (debounced, every 30 seconds)
- [ ] Manual save + publish button
- [ ] Mobile preview toggle (responsive view)
- [ ] Version history sidebar: view/restore previous versions

### Media Library
- [ ] Grid view of all uploaded assets
- [ ] Upload: drag-drop + file picker (images, videos, documents)
- [ ] Image optimization: auto-resize, convert to WebP, generate thumbnails
- [ ] Search by filename, tags, alt text
- [ ] Bulk actions: select multiple, delete, download
- [ ] Storage usage indicator
- [ ] AI alt-text generation (via LLM)
- [ ] Folder organization (optional, flat by default)

### Site Manager
- [ ] List all pages in site with status (draft/published)
- [ ] Create new page (blank or from template)
- [ ] Duplicate page
- [ ] Delete page (soft delete with 30-day recovery)
- [ ] Domain settings: custom domain connection guide, SSL status
- [ ] Global site settings: favicon, site title, analytics code
- [ ] Navigation menu builder (header menu items)
- [ ] 404 page configuration

### Template Browser
- [ ] Grid of templates with preview thumbnails
- [ ] Filter by category, niche, tags
- [ ] Search templates
- [ ] Template preview (full responsive preview)
- [ ] "Use this template" → creates new page from template
- [ ] Brand preview: see template with your colors/logo

### Notification Center
- [ ] Bell icon with unread count
- [ ] Dropdown with notification list
- [ ] Types: agent completed task, new lead/form submission, payment received, system alert
- [ ] Mark as read, mark all read
- [ ] Notification preferences (email digest, in-app, push)

### Onboarding Wizard (Setup Flow)
- [ ] Step 1: Business info (name, type/niche, description)
- [ ] Step 2: Branding (logo upload, color picker, font selection)
- [ ] Step 3: Template selection (browse by niche)
- [ ] Step 4: Domain setup (use subdomain or connect custom domain)
- [ ] Step 5: First agent interaction ("Tell me about your business in one sentence")
- [ ] Step 6: Dashboard tour (highlight key areas)
- [ ] Progress indicator on dashboard until setup complete

### Database Schema (Phase 2 additions)
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id),
    type VARCHAR(100) NOT NULL, -- agent_complete, new_lead, payment, system
    title VARCHAR(255) NOT NULL,
    body TEXT,
    data JSONB DEFAULT '{}', -- action URL, related resource
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL, -- email, push, in_app
    type VARCHAR(100) NOT NULL, -- notification type
    enabled BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, channel, type)
);

CREATE TABLE onboarding_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    step_business_info BOOLEAN DEFAULT FALSE,
    step_branding BOOLEAN DEFAULT FALSE,
    step_template BOOLEAN DEFAULT FALSE,
    step_domain BOOLEAN DEFAULT FALSE,
    step_agent_intro BOOLEAN DEFAULT FALSE,
    step_tour BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE site_navigation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    items JSONB NOT NULL DEFAULT '[]', -- [{label, url, children}]
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] Dashboard loads with sidebar, top bar, activity feed
- [ ] Command palette opens with Cmd+K, searches across app
- [ ] User can navigate to visual editor for any page
- [ ] Visual editor: add/remove/reorder blocks via drag-drop
- [ ] Each block type has a working editor panel
- [ ] Global styles (colors, fonts) apply across all blocks
- [ ] Live preview updates in real-time as edits are made
- [ ] Undo/redo works for all edits
- [ ] Auto-save works, manual save/publish works
- [ ] Media library: upload, view, search, select for use in editor
- [ ] Template browser: filter, preview, create page from template
- [ ] Onboarding wizard completes and tracks progress
- [ ] Notifications appear for agent actions and form submissions
- [ ] All UI is responsive (works on mobile/tablet/desktop)
- [ ] Dark/light mode works throughout

## Known Risks
- Visual editor complexity: Block editors are notoriously hard to get right. Consider using Plate.js or TipTap for rich text blocks.
- Drag-drop: Use dnd-kit library for reliable drag-drop in React.
- Real-time preview: Keep preview and editor state synced without performance issues.

## What's Next
After Phase 2, proceed to Phase 3 (Email/CRM) and/or Phase 5 (Calendar) — these can be built in parallel.
