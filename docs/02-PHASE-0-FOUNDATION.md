# Phase 0 — Foundation

> **Goal**: Set up all infrastructure, project scaffolding, authentication, database, and deployment pipeline. After this phase, we have a running app with login that deploys automatically.

## Status: NOT STARTED

## Checklist

### Infrastructure
- [ ] AWS Lightsail instance (Ubuntu 24.04 LTS, 2GB RAM / 2 vCPU minimum)
- [ ] Domain: agentbloom.nobleblocks.com → Lightsail IP (Route 53 CNAME/A record)
- [ ] SSL certificate (Let's Encrypt via Certbot, auto-renewal)
- [ ] S3 bucket: `agentbloom-assets` (media, uploads, generated sites)
- [ ] S3 bucket: `agentbloom-sites` (user-generated static sites)
- [ ] CloudFront distribution for S3 assets
- [ ] RDS PostgreSQL 16 instance (db.t3.micro for testing, pgvector extension enabled)
- [ ] ElastiCache Redis (cache.t3.micro for sessions/cache)
- [ ] SES domain verification for nobleblocks.com (sending test emails)
- [ ] IAM roles and policies (least privilege)

### Backend (Django)
- [ ] Django 5.x project initialization
- [ ] Django REST Framework setup
- [ ] Django Channels setup (WebSocket support)
- [ ] Database models: User, Organization, Site, Page
- [ ] Custom user model (email-based, not username)
- [ ] Django allauth: email/password + Google OAuth + magic link
- [ ] CORS configuration for frontend
- [ ] Environment variable management (.env + AWS Secrets Manager)
- [ ] Health check endpoint (`/api/health/`)
- [ ] API versioning (`/api/v1/`)
- [ ] Rate limiting (django-ratelimit)
- [ ] Logging configuration (structured JSON logs → CloudWatch)

### Frontend (Next.js)
- [ ] Next.js 15 project initialization (App Router)
- [ ] Tailwind CSS + shadcn/ui setup
- [ ] Auth pages: login, register, forgot password, magic link
- [ ] Protected route middleware
- [ ] API client (fetch wrapper with auth headers)
- [ ] Layout: sidebar + main content area + floating agent widget placeholder
- [ ] Dark/light theme support
- [ ] Error boundary + 404/500 pages
- [ ] Loading states and skeleton screens

### DevOps
- [ ] GitHub Actions CI/CD pipeline
  - [ ] Lint (ESLint + Ruff)
  - [ ] Type check (TypeScript + mypy)
  - [ ] Test (pytest + Jest)
  - [ ] Build
  - [ ] Deploy to Lightsail (SSH + rsync or Docker)
- [ ] Docker Compose for local development
- [ ] Nginx reverse proxy config (Lightsail: port 80/443 → Django 8000 + Next.js 3000)
- [ ] Process manager (systemd or PM2)

### Database Schema (Initial)
```sql
-- Core tables for Phase 0

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    password_hash TEXT, -- null for OAuth-only users
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    plan VARCHAR(50) DEFAULT 'free', -- free, starter, pro, enterprise
    timezone VARCHAR(100) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    custom_domain VARCHAR(255),
    subdomain VARCHAR(255) UNIQUE, -- orgname.agentbloom.com
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE org_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- owner, admin, member
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(org_id, user_id)
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    org_id UUID REFERENCES organizations(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] User can sign up with email/password
- [ ] User can sign in with Google OAuth
- [ ] User can request magic link login
- [ ] Authenticated user sees dashboard shell (sidebar + main area)
- [ ] Dark/light theme toggle works
- [ ] App is deployed and accessible at agentbloom.nobleblocks.com
- [ ] SSL is active (HTTPS)
- [ ] CI/CD pipeline runs on push to main
- [ ] Health check endpoint returns 200

## Known Risks
- RDS + ElastiCache cost: ~$30-40/month combined. Can use Lightsail's built-in DB for testing if needed.
- Lightsail 2GB may be tight for Django + Next.js + Nginx. Monitor and upgrade if needed.

## What's Next
After Phase 0 completion, proceed to Phase 1 (Core Agent + Page Builder).
