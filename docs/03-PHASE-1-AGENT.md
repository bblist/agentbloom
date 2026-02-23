# Phase 1 — Core Agent + Page Builder

> **Goal**: Build the AI agent reasoning loop and the page/site generation system. After this phase, a user can talk to the agent and get a generated page deployed.

## Status: NOT STARTED

## Dependencies
- Phase 0 (Foundation) must be complete

## Checklist

### Agent Core
- [ ] Agent reasoning loop (ReAct pattern): Input → Reason → Act → Observe → Loop
- [ ] LLM integration layer (abstracted provider interface)
  - [ ] Gemini 2.0 Flash/Pro connector
  - [ ] Claude Sonnet 4 connector (fallback)
  - [ ] Model switching logic (fallback on error, configurable per task)
- [ ] System prompt management (per-user context injection)
- [ ] Conversation memory (short-term: current session, long-term: DB-backed)
- [ ] Tool registry (versioned tool definitions, JSON schema for each)
- [ ] Tool executor (sandboxed execution of agent-selected tools)
- [ ] Streaming response support (token-by-token to frontend via WebSocket)
- [ ] Error handling: graceful failures, clarification requests, retry logic
- [ ] Confidence scoring: low confidence → ask user for clarification
- [ ] Agent personality config: tone (formal/casual/friendly), verbosity
- [ ] Conversation state stack (undo/rollback support)
- [ ] Per-user rate limiting (token budget tracking)
- [ ] Prompt caching (cache system prompts + KB context)
- [ ] Agent action logging (all tool calls logged with inputs/outputs)
- [ ] Scheduled tasks engine (cron-like: "every Monday send report")

### Agent Tools (Initial Set — Phase 1)
- [ ] `generate_page` — Create a new page from description + template
- [ ] `update_page` — Modify existing page content/layout
- [ ] `generate_copy` — Write editorial copy (headlines, body, CTAs)
- [ ] `generate_testimonials` — Create niche-appropriate testimonials
- [ ] `build_pricing_table` — Generate pricing tiers
- [ ] `fetch_stock_images` — Search Unsplash/Pexels API for relevant images
- [ ] `preview_page` — Generate preview URL for user approval
- [ ] `deploy_page` — Push approved page to live S3/CloudFront
- [ ] `list_templates` — Show available templates
- [ ] `select_template` — Choose template as base
- [ ] `customize_template` — Apply branding (colors, fonts, logo)

### Page Builder
- [ ] Page data model (JSONB block-based structure)
- [ ] Block types: Hero, Text, Image, CTA, Form, Pricing, Testimonials, FAQ, Footer, Gallery, Video Embed
- [ ] Template data model (reusable page configurations)
- [ ] Template storage (DB + S3 for assets)
- [ ] Page renderer: JSON blocks → HTML/CSS (server-side rendering)
- [ ] Responsive rendering (mobile, tablet, desktop breakpoints)
- [ ] Form handling: basic contact/lead forms with email notification
- [ ] Page deployment pipeline: render → optimize → upload to S3 → invalidate CloudFront cache → live
- [ ] Page versioning: auto-save snapshots, revert to any version
- [ ] SEO basics: auto-generate meta tags, OG tags, structured data
- [ ] Stock image integration (Unsplash/Pexels API)

### Initial Templates (25)
- [ ] HVAC — Emergency repair, lead form, service area, urgency CTA
- [ ] Plumbing — Leak repair promo, booking calendar placeholder, testimonials
- [ ] Electrician — Safety tips, quote request form, certifications
- [ ] Salon — Service menu, gallery, online booking CTA
- [ ] Cleaning Service — Pricing tiers, eco badges, before/after gallery
- [ ] Yoga Teacher — Class schedule, free video teaser, membership CTA
- [ ] Life Coach — E-book opt-in, testimonial slider, session booking CTA
- [ ] Fitness Instructor — Challenge funnel, progress showcase, membership
- [ ] Therapist — Calm design, confidentiality notice, booking CTA
- [ ] Online Course — Module previews, certificate badge, enrollment CTA
- [ ] Workshop — Event details, countdown, registration form
- [ ] Tutoring — Subject list, schedule, parent testimonials
- [ ] Restaurant — Menu showcase, reservation CTA, location map
- [ ] Real Estate — Property listings grid, virtual tour embed, contact
- [ ] Event Planner — RSVP form, countdown timer, gallery
- [ ] Freelancer Portfolio — Skills showcase, project gallery, contact form
- [ ] Consultant — Services grid, case studies, booking CTA
- [ ] SaaS Landing — Feature highlights, pricing, waitlist/signup
- [ ] Blog — Post layout, newsletter signup, categories sidebar
- [ ] Digital Product — Product showcase, paywall CTA, upsell
- [ ] Thank You Page — Confirmation, next steps, social sharing
- [ ] Coming Soon — Countdown, email capture, teaser
- [ ] Privacy Policy — Auto-generated compliant text
- [ ] Terms of Service — Auto-generated legal text
- [ ] 404 Page — Fun branded error page with navigation

### Chat Interface (Frontend)
- [ ] Text input with send button
- [ ] Message history display (user + agent messages)
- [ ] Streaming agent response (typing indicator → token stream)
- [ ] Tool execution display (show what agent is doing: "Generating page...")
- [ ] Page preview embed (inline preview of generated page)
- [ ] Approval buttons (Approve / Edit / Regenerate)
- [ ] Voice input button (browser Web Speech API for Phase 1, upgrade later)
- [ ] Collapsible agent reasoning panel (debug mode)
- [ ] Conversation history sidebar (past conversations)

### Database Schema (Phase 1 additions)
```sql
-- Agent tables
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant, system, tool
    content TEXT NOT NULL,
    tool_calls JSONB, -- array of tool calls made
    tool_results JSONB, -- results from tool executions
    token_count INTEGER,
    model_used VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    personality VARCHAR(50) DEFAULT 'friendly', -- formal, casual, friendly
    primary_model VARCHAR(100) DEFAULT 'gemini-2.0-flash',
    fallback_model VARCHAR(100) DEFAULT 'claude-sonnet-4',
    token_budget_daily INTEGER DEFAULT 100000,
    token_budget_monthly INTEGER DEFAULT 2000000,
    tokens_used_today INTEGER DEFAULT 0,
    tokens_used_month INTEGER DEFAULT 0,
    custom_instructions TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL,
    schedule VARCHAR(100) NOT NULL, -- cron expression
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Page/Site tables
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft', -- draft, published, archived
    settings JSONB DEFAULT '{}', -- global styles, fonts, colors, favicon
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(org_id, slug)
);

CREATE TABLE pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    page_type VARCHAR(50) DEFAULT 'landing', -- landing, funnel, blog, privacy, terms, thankyou, 404, coming_soon
    blocks JSONB NOT NULL DEFAULT '[]', -- ordered array of block objects
    seo_title VARCHAR(255),
    seo_description TEXT,
    og_image_url TEXT,
    schema_markup JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    published_url TEXT,
    custom_css TEXT,
    custom_js TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    UNIQUE(site_id, slug)
);

CREATE TABLE page_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    blocks JSONB NOT NULL,
    seo_title VARCHAR(255),
    seo_description TEXT,
    change_description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL, -- local_services, wellness, education, etc.
    niche VARCHAR(100), -- hvac, yoga, restaurant, etc.
    description TEXT,
    preview_image_url TEXT,
    blocks JSONB NOT NULL DEFAULT '[]',
    default_settings JSONB DEFAULT '{}', -- colors, fonts
    tags TEXT[] DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL, -- hero, cta, pricing, testimonial, footer, etc.
    description TEXT,
    preview_image_url TEXT,
    block_definition JSONB NOT NULL, -- single block definition
    variants JSONB DEFAULT '[]', -- style variants
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE media_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_type VARCHAR(50) NOT NULL, -- image, video, document, audio
    mime_type VARCHAR(100),
    file_size BIGINT,
    s3_key TEXT NOT NULL,
    cdn_url TEXT,
    alt_text TEXT,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}', -- dimensions, duration, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    fields JSONB NOT NULL DEFAULT '[]', -- field definitions
    settings JSONB DEFAULT '{}', -- redirect URL, notification email, etc.
    submission_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE form_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_id UUID REFERENCES forms(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    ip_address INET,
    user_agent TEXT,
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] User can open agent chat and type a command
- [ ] Agent processes command through ReAct loop
- [ ] Agent can select and use tools (generate_page, fetch_stock_images, etc.)
- [ ] Agent generates a complete page with copy, images, pricing
- [ ] User sees real-time streaming response from agent
- [ ] User can preview generated page before deploying
- [ ] User can approve → page deploys to S3 and is publicly accessible
- [ ] Agent shows reasoning steps in debug panel
- [ ] Agent asks clarification when uncertain
- [ ] Agent handles errors gracefully ("I couldn't do X, would you like to try Y?")
- [ ] User can browse and select from 25 templates
- [ ] Agent can customize template based on user's business
- [ ] Page versions are saved and user can revert
- [ ] Generated pages are mobile-responsive
- [ ] Basic SEO (meta tags, OG) auto-generated

## Known Risks
- LLM API costs: Gemini Flash is cheap (~$0.075/1M input tokens), but heavy agent loops could add up. Monitor.
- Template quality: 25 templates is a lot of front-end work. Consider hiring a designer or using high-quality open-source templates as starting points.
- Page rendering: Server-side JSON → HTML rendering needs careful design to handle all block types well.

## What's Next
After Phase 1 completion, proceed to Phase 2 (Dashboard + Visual Editor).
