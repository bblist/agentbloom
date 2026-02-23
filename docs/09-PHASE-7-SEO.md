# Phase 7 — SEO Engine

> **Goal**: Automated SEO optimization for all generated content — schema markup, meta tags, sitemaps, page speed, local SEO, and AI search readiness. After this phase, every page is search-engine optimized automatically.

## Status: NOT STARTED

## Dependencies
- Phase 1 (Agent + Pages) — page data model

## Checklist

### Auto-SEO (Runs on Every Page Publish)
- [ ] Meta title generation (LLM-generated, 50-60 chars, keyword-optimized)
- [ ] Meta description generation (LLM-generated, 150-160 chars)
- [ ] Canonical URL setting
- [ ] Open Graph tags: title, description, image, URL, type
- [ ] Twitter Card tags
- [ ] Heading hierarchy validation (H1 → H2 → H3, no skips)

### Schema Markup (JSON-LD)
- [ ] Auto-detect page type → apply appropriate schema:
  - [ ] LocalBusiness (HVAC, plumbing, salon, etc.)
  - [ ] Course (online courses)
  - [ ] Event (workshops, classes)
  - [ ] Person (coaches, instructors)
  - [ ] Product (digital products)
  - [ ] FAQPage (FAQ sections)
  - [ ] HowTo (tutorial content)
  - [ ] Recipe (food bloggers)
  - [ ] Service (service pages)
  - [ ] Organization (about pages)
  - [ ] BreadcrumbList (all multi-page sites)
  - [ ] WebSite + SearchAction (main pages)
- [ ] Schema validation before deploy
- [ ] Custom schema override (advanced users)

### Sitemap & Robots
- [ ] Auto-generate XML sitemap on page publish/unpublish
- [ ] Sitemap submission to Google Search Console (API)
- [ ] robots.txt generation with sensible defaults
- [ ] robots.txt manual override
- [ ] Per-page noindex/nofollow toggle

### Page Speed Optimization
- [ ] Image optimization: auto-convert to WebP/AVIF, auto-resize, lazy loading
- [ ] CSS minification for generated pages
- [ ] JS minification for generated pages
- [ ] HTML minification
- [ ] Preload critical resources hint
- [ ] CDN delivery via CloudFront (already in place)
- [ ] Performance score display (Lighthouse-style, calculated server-side)
- [ ] Core Web Vitals monitoring (CLS, LCP, FID/INP)

### Local SEO (Critical for Service Businesses)
- [ ] NAP consistency checker (Name, Address, Phone across pages)
- [ ] Service area schema
- [ ] Local business schema with hours, area served
- [ ] Google Business Profile optimization tips
- [ ] Location-specific landing pages (agent generates for each service area)
- [ ] "Near me" keyword integration suggestions

### Google Integrations
- [ ] Google Search Console connection (OAuth)
- [ ] Search Console data: impressions, clicks, CTR, position by page/keyword
- [ ] Google Analytics 4 connection
- [ ] GA4 data: traffic, sources, conversions in dashboard
- [ ] Google Keyword Planner data (via Ads API): search volume, competition, CPC

### SEO Audit Tool
- [ ] Per-page audit: check meta tags, headings, alt text, links, content length
- [ ] Site-wide audit: broken links, duplicate titles, missing descriptions, orphan pages
- [ ] Issue severity: critical, warning, info
- [ ] Fix suggestions: agent can auto-fix most issues
- [ ] Audit history: track improvement over time

### AI Search Optimization (2026)
- [ ] Content structured for LLM consumption:
  - [ ] Clear question-answer format in FAQ sections
  - [ ] Entity-rich content (people, organizations, services explicitly named)
  - [ ] Authoritative sources cited
  - [ ] Structured summaries at top of long content
- [ ] E-E-A-T signals:
  - [ ] Author bio sections on content pages
  - [ ] Credentials/certifications highlighted
  - [ ] Customer reviews/testimonials with schema
  - [ ] "About" and "Contact" pages recommended

### Rank Tracking
- [ ] Track target keywords per page/site
- [ ] Weekly position snapshots (via Search Console data)
- [ ] Rank change alerts (improved/dropped significantly)
- [ ] Keyword suggestions from agent

### Agent Tools (Phase 7)
- [ ] `optimize_seo` — Run SEO optimization on a page
- [ ] `run_seo_audit` — Audit a page or whole site
- [ ] `keyword_research` — Research keywords for a topic/niche
- [ ] `generate_local_pages` — Create service-area specific pages
- [ ] `check_rankings` — Show current keyword rankings

### Database Schema (Phase 7 additions)
```sql
CREATE TABLE seo_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    google_sc_connected BOOLEAN DEFAULT FALSE,
    google_analytics_id VARCHAR(50),
    google_sc_property VARCHAR(255),
    default_og_image TEXT,
    robots_txt TEXT,
    custom_head_code TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE seo_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    page_id UUID REFERENCES pages(id),
    audit_type VARCHAR(50) NOT NULL, -- page, site
    score INTEGER, -- 0-100
    issues JSONB NOT NULL DEFAULT '[]', -- [{type, severity, message, fix_suggestion}]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tracked_keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    page_id UUID REFERENCES pages(id),
    current_position INTEGER,
    previous_position INTEGER,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5,2) DEFAULT 0,
    last_checked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site_id, keyword)
);

CREATE TABLE google_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    service_type VARCHAR(50) NOT NULL, -- search_console, analytics, ads
    account_email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    property_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] Every published page has auto-generated meta tags and OG tags
- [ ] Appropriate schema markup added based on page type
- [ ] Sitemap auto-generates and updates on publish
- [ ] Images auto-optimized (WebP, lazy loading)
- [ ] SEO audit tool finds and reports issues
- [ ] Google Search Console data displayed in dashboard
- [ ] Keyword research tool provides useful data
- [ ] Local SEO features generate appropriate schema and content
- [ ] Performance score displayed per page
- [ ] Agent can run SEO tasks via commands

## Known Risks
- Google API quotas: Search Console API has daily quotas. Cache data aggressively (refresh daily, not per-request).
- Keyword Planner: Requires active Google Ads account. May need workaround for users without one.
- Lighthouse scoring: Running Lighthouse server-side is resource-intensive. Consider using PageSpeed Insights API instead.

## What's Next
Phase 8 (Knowledge Base) — can be built in parallel with this phase.
