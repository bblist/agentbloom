# AgentBloom

**"Speak it. Build it. Bloom."**

The voice-first AI platform that turns one sentence into a fully built, hosted, and managed online business.

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (with pgvector extension)
- Redis

### Development Setup

```bash
# Clone
git clone https://github.com/bblist/agentbloom.git
cd agentbloom

# Backend
cd backend
cp .env.example .env  # Edit with your API keys
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (new terminal)
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### Docker (recommended)
```bash
docker compose up --build
```

App: http://localhost:3000
API: http://localhost:8000
Admin: http://localhost:8000/admin/

## Project Structure

```
agentbloom/
├── docs/                   # Phase plans + architecture docs
├── backend/                # Django 5.x backend
│   ├── agentbloom/        # Django project config
│   ├── apps/              # Django apps
│   │   ├── users/         # Auth, users, orgs
│   │   ├── sites/         # Sites, pages, templates
│   │   ├── agent/         # AI agent engine
│   │   ├── email_crm/     # Email, CRM, campaigns
│   │   ├── courses/       # Courses, memberships
│   │   ├── calendar/      # Bookings, events
│   │   ├── payments/      # Stripe, billing
│   │   ├── kb/            # Knowledge base
│   │   ├── seo/           # SEO engine
│   │   └── admin_panel/   # Platform admin
│   ├── manage.py
│   └── requirements.txt
├── frontend/              # Next.js 15+ frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # Shared components
│   │   ├── lib/          # Utilities
│   │   └── styles/       # Global styles
│   ├── package.json
│   └── next.config.js
├── deploy/                # Deployment configs
├── scripts/               # Dev scripts
├── docker-compose.yml
└── README.md
```

## Documentation

| Document | Description |
|----------|-----------|
| [Product Vision](docs/00-VISION.md) | Core concept, target users, value prop |
| [Feature Analysis](docs/01-FEATURE-ANALYSIS.md) | Every feature reviewed with gaps/additions |
| [Phase Master Plan](docs/01-PHASE-MASTER.md) | All phases, dependencies, timeline |
| [Phase 0: Foundation](docs/02-PHASE-0-FOUNDATION.md) | Infrastructure, auth, DB, scaffold |
| [Phase 1: Agent + Pages](docs/03-PHASE-1-AGENT.md) | AI agent, page builder, templates |
| [Phase 2: Dashboard](docs/04-PHASE-2-DASHBOARD.md) | Dashboard UI, visual editor |
| [Phase 3: Email/CRM](docs/05-PHASE-3-EMAIL-CRM.md) | Email marketing, contacts, automation |
| [Phase 4: Courses](docs/06-PHASE-4-COURSES.md) | Course builder, memberships, community |
| [Phase 5: Calendar](docs/07-PHASE-5-CALENDAR.md) | Booking system, availability |
| [Phase 6: Payments](docs/08-PHASE-6-PAYMENTS.md) | Stripe Connect, subscriptions, invoicing |
| [Phase 7: SEO](docs/09-PHASE-7-SEO.md) | Auto-SEO, schema, audits |
| [Phase 8: Knowledge Base](docs/10-PHASE-8-KNOWLEDGE-BASE.md) | Upload, process, embed, search |
| [Phase 9: Admin](docs/11-PHASE-9-ADMIN.md) | Platform admin panel |
| [Phase 10: Polish](docs/12-PHASE-10-POLISH.md) | Testing, performance, launch prep |
| [Phase 11: AI Receptionist](docs/13-PHASE-11-RECEPTIONIST.md) | Voice/chat AI (add-on, last) |
| [Architecture](docs/14-ARCHITECTURE.md) | System diagrams, data flow |
| [Decisions & Risks](docs/15-DECISIONS-RISKS.md) | Key trade-offs, cost projections |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x + DRF + Channels |
| Frontend | Next.js 15+ + Tailwind + shadcn/ui |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis |
| Auth | Django allauth |
| LLM | GPT-4o + Claude 4.6 + Gemini 3.2 Pro |
| Email | AWS SES |
| Storage | AWS S3 + CloudFront |
| DNS | AWS Route 53 |
| Hosting | AWS Lightsail → ECS |
| CI/CD | GitHub Actions |

## Infrastructure

- **Testing**: agentbloom.nobleblocks.com (Lightsail @ 52.1.31.54)
- **GitHub**: https://github.com/bblist/agentbloom

## License

Proprietary - All rights reserved.
