# Phase 6 — Payments & Billing

> **Goal**: Implement Stripe Connect, checkout flows, subscriptions, invoicing, and platform billing. After this phase, users can accept payments for courses, bookings, and memberships.

## Status: NOT STARTED

## Dependencies
- Phase 0 (Foundation)
- Phase 4 (Courses) — course pricing
- Phase 5 (Calendar) — booking payments

## Checklist

### Stripe Connect Integration
- [ ] Platform Stripe account setup (Connected accounts model)
- [ ] User onboarding: Stripe Connect Express (simplified onboarding for users)
- [ ] Account status tracking: pending, active, restricted, disabled
- [ ] KYC/identity verification flow guidance
- [ ] Platform fee: configurable % per transaction (e.g., 5%)
- [ ] Auto-payouts: daily/weekly to user's connected account
- [ ] Direct charge model (funds go to connected account, platform takes fee)

### Checkout System
- [ ] Stripe Checkout (hosted) for simplicity
- [ ] Embedded checkout (Stripe Elements) for branded experience
- [ ] Checkout page builder: customize colors, add testimonials, trust badges
- [ ] Product/price management: one-time, recurring (monthly/yearly)
- [ ] Free trials: X days free then charge
- [ ] Coupons/promo codes: % off, $ off, recurring, one-time, limited use, expiry date
- [ ] Order bumps: add-on offer during checkout (e.g., "Add VIP access for $19")
- [ ] Post-purchase upsell page: one-click add after initial purchase
- [ ] Quantity selection (for products, not services)
- [ ] Tax calculation: Stripe Tax or manual tax rules per region

### Subscription Management
- [ ] Create subscription products (tied to membership tiers)
- [ ] Subscription lifecycle: trial → active → past_due → cancelled → expired
- [ ] Dunning management:
  - [ ] Auto-retry failed payments (3 attempts over 7 days)
  - [ ] Failed payment email notifications to customer
  - [ ] Grace period before access revocation
- [ ] Proration: upgrade/downgrade mid-cycle
- [ ] Cancellation flow: immediate or end-of-period
- [ ] Reactivation: re-subscribe after cancellation
- [ ] Stripe Customer Portal: self-service billing for subscribers

### Invoicing
- [ ] Auto-generate invoice on payment (PDF)
- [ ] Invoice template: business name, logo, items, total, payment status
- [ ] Invoice numbering: sequential (INV-001, INV-002, etc.)
- [ ] Invoice email: auto-send on payment/subscription renewal
- [ ] Manual invoice creation (for custom services)
- [ ] Invoice list view with search, filter, download

### Refund Management
- [ ] Refund request handling (manual approval)
- [ ] Full or partial refund
- [ ] Refund reason tracking
- [ ] Auto-revoke access on refund (courses, memberships)
- [ ] Refund notification email

### Revenue Dashboard
- [ ] Total revenue: daily, weekly, monthly, yearly
- [ ] Revenue by product/course/membership/booking
- [ ] MRR (Monthly Recurring Revenue) tracking
- [ ] Churn rate calculation
- [ ] Transaction history: all payments with status, source, amount
- [ ] Payout history: all payouts to user's bank account
- [ ] Revenue charts: line graphs, bar charts
- [ ] Export: CSV download for accounting

### Platform Billing (our billing)
- [ ] Plan tiers: Free, Starter ($29/mo), Pro ($79/mo), Enterprise (custom)
- [ ] Feature gates per plan (page limits, email sends, storage, etc.)
- [ ] Usage tracking: pages created, emails sent, storage used, agent tokens
- [ ] Upgrade/downgrade flows
- [ ] Platform subscription via Stripe
- [ ] Trial period for new signups (14 days)

### PayPal Integration (Phase 6b)
- [ ] PayPal checkout button
- [ ] PayPal subscription creation
- [ ] Webhook handling (payment complete, subscription cancelled, etc.)
- [ ] PayPal payouts for users who prefer PayPal

### Agent Tools (Phase 6)
- [ ] `setup_payments` — Connect user's Stripe account
- [ ] `create_product` — Create product with pricing
- [ ] `create_coupon` — Generate promo code
- [ ] `view_revenue` — Show revenue dashboard data
- [ ] `setup_subscription` — Configure subscription product
- [ ] `issue_refund` — Process refund for a payment

### Database Schema (Phase 6 additions)
```sql
CREATE TABLE stripe_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    stripe_account_id VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) DEFAULT 'express', -- express, standard, custom
    status VARCHAR(50) DEFAULT 'pending', -- pending, active, restricted, disabled
    capabilities JSONB DEFAULT '{}',
    payouts_enabled BOOLEAN DEFAULT FALSE,
    charges_enabled BOOLEAN DEFAULT FALSE,
    country VARCHAR(2),
    default_currency VARCHAR(3),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    product_type VARCHAR(50) NOT NULL, -- course, membership, booking, digital, physical, service
    stripe_product_id VARCHAR(255),
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    stripe_price_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    pricing_type VARCHAR(50) NOT NULL, -- one_time, recurring
    interval VARCHAR(20), -- month, year (for recurring)
    trial_days INTEGER DEFAULT 0,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    code VARCHAR(50) UNIQUE NOT NULL,
    stripe_coupon_id VARCHAR(255),
    discount_type VARCHAR(20) NOT NULL, -- percent, amount
    discount_value DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD', -- for amount discounts
    applies_to JSONB DEFAULT '{}', -- {product_ids: [...]} or all
    max_uses INTEGER, -- null = unlimited
    uses_count INTEGER DEFAULT 0,
    duration VARCHAR(20) DEFAULT 'once', -- once, forever, repeating
    duration_months INTEGER, -- for repeating
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    product_id UUID REFERENCES products(id),
    price_id UUID REFERENCES prices(id),
    stripe_payment_intent_id VARCHAR(255),
    stripe_checkout_session_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    platform_fee DECIMAL(10,2) DEFAULT 0,
    net_amount DECIMAL(10,2), -- amount - platform_fee
    status VARCHAR(50) NOT NULL, -- pending, succeeded, failed, refunded, partially_refunded
    payment_method VARCHAR(50), -- card, paypal, etc.
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    coupon_id UUID REFERENCES coupons(id),
    metadata JSONB DEFAULT '{}',
    receipt_url TEXT,
    invoice_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    product_id UUID REFERENCES products(id),
    price_id UUID REFERENCES prices(id),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active', -- trialing, active, past_due, cancelled, unpaid, expired
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    dunning_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    payment_id UUID REFERENCES payments(id),
    invoice_number VARCHAR(50) NOT NULL,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_address JSONB,
    items JSONB NOT NULL DEFAULT '[]', -- [{description, quantity, unit_price, total}]
    subtotal DECIMAL(10,2),
    tax DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'paid', -- draft, sent, paid, void
    pdf_url TEXT,
    due_date DATE,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(org_id, invoice_number)
);

CREATE TABLE payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    stripe_payout_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL, -- pending, in_transit, paid, failed, cancelled
    arrival_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Platform billing (our charges to users)
CREATE TABLE platform_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    stripe_product_id VARCHAR(255),
    stripe_price_monthly VARCHAR(255),
    stripe_price_yearly VARCHAR(255),
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2) NOT NULL,
    features JSONB NOT NULL DEFAULT '{}',
    limits JSONB NOT NULL DEFAULT '{}', -- {pages: 10, emails_per_month: 1000, storage_gb: 5}
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE platform_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES platform_plans(id),
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'trialing',
    trial_ends_at TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    pages_created INTEGER DEFAULT 0,
    emails_sent INTEGER DEFAULT 0,
    storage_used_bytes BIGINT DEFAULT 0,
    agent_tokens_used INTEGER DEFAULT 0,
    video_minutes_hosted INTEGER DEFAULT 0,
    bookings_made INTEGER DEFAULT 0,
    UNIQUE(org_id, period_start)
);
```

## Acceptance Criteria
- [ ] User can connect Stripe account (Connect Express flow)
- [ ] User can create products with one-time or recurring pricing
- [ ] Stripe Checkout works for purchases
- [ ] Subscriptions lifecycle (trial → active → cancel) works
- [ ] Dunning emails send on failed payments
- [ ] Coupons/promo codes apply correctly
- [ ] Invoices auto-generate and email to customers
- [ ] Revenue dashboard shows accurate metrics
- [ ] Refunds process and revoke access
- [ ] Platform billing (our plans) works
- [ ] Agent can create products and coupons via commands
- [ ] PayPal checkout works (Phase 6b)

## Known Risks
- Stripe Connect compliance: Each country has different requirements. Start with US/UK/EU.
- Platform fee split: Stripe charges on top of platform fee. Make sure pricing accounts for this.
- Subscription webhooks: Must reliably handle all Stripe events. Use Stripe webhook endpoint with signature verification.
- Tax: Automated tax calculation adds complexity. Start with manual tax rules, upgrade to Stripe Tax later.

## What's Next
Phase 7 (SEO Engine) and Phase 8 (Knowledge Base) — can be parallel.
