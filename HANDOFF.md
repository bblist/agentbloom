# AgentBloom — Phase 7 Handoff: Production Deployment

## Deployment Status: ✅ LIVE

**URL**: https://bloom.nobleblocks.com
**Admin**: https://bloom.nobleblocks.com/admin/
**API**: https://bloom.nobleblocks.com/api/v1/

---

## Infrastructure

| Component | Details |
|-----------|---------|
| **Hosting** | AWS Lightsail `agentbloom` instance, medium_3_0 (4GB RAM, 2 vCPU, 80GB SSD) |
| **OS** | Ubuntu 24.04 LTS |
| **IP** | 52.1.31.54 |
| **Domain** | bloom.nobleblocks.com (Route 53 A record) |
| **SSL** | Let's Encrypt via Certbot (auto-renewal configured) |
| **Cost** | ~$20/month (well under $50 budget) |

## Architecture

```
Internet → Nginx (host, port 80/443)
           ├── /api/*, /admin/*, /ws/* → backend:8000 (Django/Daphne ASGI)
           └── /* → frontend:3000 (Next.js standalone)

Docker Containers (6):
  db        — PostgreSQL 16 + pgvector (persistent volume)
  redis     — Redis 7 Alpine (256MB limit)
  backend   — Django 5.1 + DRF + Channels + Daphne
  frontend  — Next.js 15 (standalone mode)
  celery    — Celery worker
  celery-beat — Celery beat scheduler
```

## Access

| What | Value |
|------|-------|
| **SSH** | `ssh -i ~/.ssh/lightsail-admasterpro.pem ubuntu@52.1.31.54` |
| **Project dir** | `/home/ubuntu/agentbloom` |
| **Superuser** | `admin@nobleblocks.com` / `AgentBloom2024!` |
| **DB name** | `agentbloom` |
| **DB user** | `agentbloom` |
| **GitHub** | https://github.com/bblist/agentbloom |

## Key Files on Server

| File | Purpose |
|------|---------|
| `/home/ubuntu/agentbloom/.env` | Production environment variables (secrets) |
| `/home/ubuntu/agentbloom/docker-compose.prod.yml` | Docker Compose config |
| `/etc/nginx/sites-available/agentbloom` | Nginx reverse proxy config |
| `/etc/letsencrypt/live/bloom.nobleblocks.com/` | SSL certificates |

## Common Operations

```bash
# SSH into server
ssh -i ~/.ssh/lightsail-admasterpro.pem ubuntu@52.1.31.54

# View running containers
cd /home/ubuntu/agentbloom
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f celery

# Rebuild and restart after code changes
git pull origin main
docker compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker compose -f docker-compose.prod.yml exec -it backend python manage.py createsuperuser

# Django shell
docker compose -f docker-compose.prod.yml exec backend python manage.py shell

# Database shell
docker compose -f docker-compose.prod.yml exec db psql -U agentbloom -d agentbloom

# Restart Nginx
sudo systemctl restart nginx

# Check SSL renewal
sudo certbot renew --dry-run
```

## API Keys Required (add to .env on server)

The following API keys are needed for full functionality:

| Key | Purpose | Required |
|-----|---------|----------|
| `OPENAI_API_KEY` | AI agent engine (GPT-4) | Yes — core feature |
| `STRIPE_SECRET_KEY` | Payment processing | Yes — for payments |
| `STRIPE_PUBLISHABLE_KEY` | Frontend Stripe.js | Yes — for payments |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook verification | Yes — for payments |
| `AWS_ACCESS_KEY_ID` | S3 uploads, SES email | Yes — for file storage/email |
| `AWS_SECRET_ACCESS_KEY` | S3 uploads, SES email | Yes — for file storage/email |
| `ANTHROPIC_API_KEY` | Claude fallback LLM | Optional |
| `GOOGLE_API_KEY` | Gemini fallback LLM | Optional |

## Phase 7 Commits

| Commit | Description |
|--------|-------------|
| `4cba5b4` | Production deployment setup (Docker, Nginx, env configs) |
| `d0075d3` | Add package-lock.json for reproducible builds |
| `b0680ca` | Fix TypeScript String() wrapper issue |
| `6b0fc3d` | Add frontend public directory |
| `a68b594` | Fix sites app label conflict (sites → site_builder) |
| `8c32c9e` | Fix timezone field shadowing in User/CalendarBooking models |
| `0276339` | Add PyJWT dependency for allauth socialaccount |
| `43b1d77` | Fix admin_panel User model field references |
| `61d7537` | Fix SEO model FK references (sites → site_builder) |
| `0237d84` | Map backend/frontend ports to localhost for Nginx |
| `692d4a4` | Add initial migration files for all 12 apps |

## Bugs Fixed During Deployment

1. **Timezone field shadowing** — `timezone` field on User/CalendarBooking models shadowed the `timezone` module import → renamed import alias
2. **Missing PyJWT** — `allauth.socialaccount` requires PyJWT for JWT kit → added to requirements.txt
3. **admin_panel field errors** — Custom User model uses `created_at` not `date_joined`, `full_name` not `first_name/last_name` → updated serializer/viewset
4. **SEO model FK references** — Sites app label changed to `site_builder` but SEO models still referenced `sites.Page/Site` → updated all 8 ForeignKey references
5. **Docker expose vs ports** — `expose` only works between containers, not for host Nginx → changed to `ports: ["127.0.0.1:XXXX:XXXX"]`
6. **pgvector extension** — Database needed `CREATE EXTENSION IF NOT EXISTS vector;` before migrations

## Known Non-Critical Issues

- **structlog warning**: `TypeError: 'str' object is not callable` in log formatting — cosmetic, doesn't affect functionality
- **allauth deprecation**: `ACCOUNT_AUTHENTICATION_METHOD` → `ACCOUNT_LOGIN_METHODS` (future allauth version)

## What's Next

- Configure API keys for full AI agent functionality
- Set up AWS SES for transactional email
- Configure S3 bucket CORS for file uploads
- Set up Stripe Connect for payment processing
- Monitor and scale as needed (Lightsail instance can be upgraded)
- Set up GitHub Actions CI/CD pipeline
- Configure automated backups for PostgreSQL data volume
