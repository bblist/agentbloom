# AgentBloom — Key Decisions, Trade-offs & Risks

## Architecture Decisions

### 1. Django vs Node.js (Backend)
**Decision**: Django 5.x (with Channels for real-time)

| Factor | Django | Node.js |
|--------|--------|---------|
| Speed to build | ✅ Admin, ORM, auth built-in | ❌ More boilerplate |
| Real-time | ⚠️ Django Channels (works, adds complexity) | ✅ Native async/WebSocket |
| Python AI ecosystem | ✅ Direct LLM library access | ❌ Need Python microservices |
| Team familiarity | ✅ Large talent pool | ✅ Also large |
| Performance | ⚠️ Adequate for 10K users | ✅ Better for I/O-heavy |

**Rationale**: Python ecosystem for AI/ML tools (langsmith, transformers, etc.) and Django's batteries-included approach (admin panel, ORM, auth) save significant development time. Channels handles WebSocket needs adequately.

### 2. Next.js + Django (separate frontend/backend) vs Django full-stack
**Decision**: Separate Next.js frontend + Django API backend

**Rationale**: 
- Better developer experience and modern UI capabilities
- SEO via Next.js SSR for public-facing pages
- Independent scaling (frontend on CDN, backend on compute)
- Industry standard for SaaS in 2026

### 3. pgvector vs Pinecone/Weaviate (Vector DB)
**Decision**: pgvector (PostgreSQL extension)

**Rationale**:
- One less service to manage and pay for
- Adequate performance for up to ~1M vectors (more than enough for years)
- HNSW index provides fast approximate search
- Upgrade path: migrate to Pinecone if pgvector becomes bottleneck

### 4. LLM Strategy
**Decision**: GPT-4o (primary, balanced cost/quality), Claude 4.6 (fallback, premium quality), Gemini 3.2 Pro (design tasks)

| Model | Cost (per 1M tokens) | Speed | Quality | Use Case |
|-------|---------------------|-------|---------|----------|
| GPT-4o | ~$2.50 input / $10.00 output | Fast | Excellent | Day-to-day agent tasks, reasoning |
| Claude 4.6 | ~$3.00 input / $15.00 output | Fast | Excellent | Fallback, creative content, complex reasoning |
| Gemini 3.2 Pro | ~$1.25 input / $5.00 output | Fast | Excellent | Design generation, visual layouts, UI/UX |

**Strategy**: Default to GPT-4o for general agent tasks — excellent tool use, reliable structured output, strong reasoning. Claude 4.6 as fallback for when OpenAI is down or for tasks requiring nuanced creative writing. Gemini 3.2 Pro for design-oriented tasks (layout generation, color schemes, visual recommendations). Users can configure preference per organization.

### 5. Hosting: Lightsail vs ECS/EC2
**Decision**: Start with Lightsail, migrate to ECS when scaling demands it

**Rationale**:
- Lightsail: simple, predictable pricing ($10-40/month), easy setup
- Sufficient for testing and first 100 users
- Migration path: Docker-based from day 1, so ECS migration is straightforward

### 6. Email: SES vs SendGrid/Mailgun
**Decision**: AWS SES

**Rationale**:
- Cheapest option ($0.10 per 1,000 emails)
- Already in AWS ecosystem
- Supports custom domain sending (DKIM/SPF)
- Drawback: requires warm-up, starts in sandbox mode

### 7. Telephony: Twilio vs Telnyx vs Plivo
**Decision**: Telnyx (if needed), starting with web chat only

| Provider | Voice (per min) | SMS (per msg) | Pros |
|----------|----------------|---------------|------|
| Twilio | $0.0085-0.022 | $0.0079 | Most popular, best docs |
| Telnyx | $0.005-0.015 | $0.004 | Cheaper, mission-grade |
| Plivo | $0.005-0.015 | $0.005 | Cheapest, good API |

**Strategy**: Start with web chat widget (zero cost). Add Telnyx for voice when demand is proven.

---

## Critical Risks & Mitigations

### Risk 1: LLM API Cost Spiral
**Risk**: Heavy agent usage drives LLM API costs beyond budget
**Mitigation**:
- Per-user daily/monthly token budgets
- Prompt caching (Redis) for repeated context
- Use Flash model for 90% of tasks
- Smart context truncation (don't send entire KB every time)
- Monitor costs daily via LLM provider dashboards

### Risk 2: Email Deliverability
**Risk**: Emails from new/user domains land in spam
**Mitigation**:
- Automated DKIM/SPF/DMARC setup guidance
- Warmup scheduler (gradual volume increase)
- Deliverability dashboard (bounce/complaint rates)
- Dedicated IPs for high-volume senders (future)
- Content scanning to avoid spam triggers

### Risk 3: Multi-tenant Data Leakage
**Risk**: One user sees another user's data
**Mitigation**:
- Mandatory org_id filter on every database query (enforced via Django middleware/manager)
- S3 bucket policies per organization
- Row-level security in PostgreSQL (additional layer)
- Automated tests that verify cross-org isolation
- Audit logs for all data access

### Risk 4: Agent Generating Harmful/Wrong Content
**Risk**: Agent creates misleading, false, or offensive content
**Mitigation**:
- Preview-before-deploy for all agent outputs
- Content moderation scanning before publish
- User approval required for live changes
- Undo/rollback capability
- Agent disclaimer: "AI-generated content, review before publishing"

### Risk 5: Video Storage Costs
**Risk**: Course videos consume massive S3 storage
**Mitigation**:
- Storage limits per plan tier (5GB free, 50GB pro, 500GB enterprise)
- Video compression (MediaConvert to 720p default)
- Usage tracking dashboard
- Inactive course archival policy

### Risk 6: Stripe Connect Compliance
**Risk**: Platform payment model has regulatory requirements
**Mitigation**:
- Use Stripe Connect Express (Stripe handles most KYC)
- Platform terms of service clearly define responsibilities
- Monitor for suspicious activity
- Country-specific compliance research before expanding

---

## Technical Debt Accepted (Consciously)

| Debt | Why Accepted | Payback Plan |
|------|-------------|-------------|
| No microservices | Complexity overhead not worth it early | Split when single service becomes bottleneck |
| Limited test coverage initially | Speed to market | Increase to 80%+ in Phase 10 |
| No Kubernetes | Over-engineering for current scale | Migrate when >1000 concurrent users |
| Basic search (pgvector only) | Good enough | Add Elasticsearch if search quality needs improvement |
| No CDN for API | Lightsail handles traffic fine | Add API caching layer when needed |

---

## Cost Projections

### Phase 0-2 (Development/Testing): ~$30-50/month
| Service | Cost |
|---------|------|
| Lightsail (4GB instance) | $24 |
| RDS (db.t3.micro) | $15 |
| ElastiCache (cache.t3.micro) | $12 |
| S3 + CloudFront | ~$2 |
| Route 53 | ~$1 |
| SES | ~$0 (low volume) |
| LLM APIs (development) | ~$10-20 |
| **Total** | **~$64-74** |

### Optimized: Use Lightsail built-in database instead of RDS → saves $15
### Optimized: Use Redis on Lightsail instead of ElastiCache → saves $12
### Optimized total: ~$37-47/month

### First 100 users: ~$100-200/month
| Service | Cost |
|---------|------|
| Lightsail (8GB instance) | $48 |
| RDS (db.t3.small) | $30 |
| ElastiCache | $12 |
| S3 + CloudFront | ~$10 |
| SES | ~$5 |
| LLM APIs | ~$50-100 |
| **Total** | **~$155-205** |

### First 1000 users: ~$500-1000/month
Move to ECS, RDS multi-AZ, etc.
