import uuid
from django.db import models
from django.utils import timezone


class StripeConnection(models.Model):
    """Stripe Connect account for an organization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.OneToOneField("users.Organization", on_delete=models.CASCADE, related_name="stripe_connection")
    stripe_account_id = models.CharField(max_length=255, unique=True)
    account_type = models.CharField(max_length=50, default="express")  # express, standard, custom
    charges_enabled = models.BooleanField(default=False)
    payouts_enabled = models.BooleanField(default=False)
    details_submitted = models.BooleanField(default=False)
    onboarding_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stripe_connections"

    def __str__(self):
        return f"Stripe: {self.stripe_account_id} ({self.org.name})"


class Product(models.Model):
    """Stripe-synced product."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="products")
    stripe_product_id = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name


class Price(models.Model):
    """Stripe-synced price."""

    BILLING_PERIOD_CHOICES = [
        ("one_time", "One Time"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    stripe_price_id = models.CharField(max_length=255, blank=True)
    amount = models.IntegerField()  # In cents
    currency = models.CharField(max_length=3, default="usd")
    billing_period = models.CharField(max_length=50, choices=BILLING_PERIOD_CHOICES, default="one_time")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "prices"

    def __str__(self):
        return f"${self.amount / 100:.2f}/{self.billing_period}"


class Coupon(models.Model):
    """Discount coupon."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="coupons")
    code = models.CharField(max_length=50)
    stripe_coupon_id = models.CharField(max_length=255, blank=True)
    discount_type = models.CharField(max_length=50, choices=[
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_redemptions = models.IntegerField(default=0)  # 0 = unlimited
    times_redeemed = models.IntegerField(default=0)
    # Restrictions
    applies_to_products = models.ManyToManyField(Product, blank=True, related_name="coupons")  # Empty = all products
    first_purchase_only = models.BooleanField(default=False)
    min_purchase_amount = models.IntegerField(default=0)  # cents
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "coupons"
        unique_together = ("org", "code")

    def __str__(self):
        return f"{self.code}: {self.discount_value}{'%' if self.discount_type == 'percentage' else ' off'}"


class Payment(models.Model):
    """Payment record."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="payments")
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    amount = models.IntegerField()  # cents
    currency = models.CharField(max_length=3, default="usd")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    customer_email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    refunded_amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]


class Subscription(models.Model):
    """Stripe subscription."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("cancelled", "Cancelled"),
        ("trialing", "Trialing"),
        ("paused", "Paused"),
        ("unpaid", "Unpaid"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="subscriptions")
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    customer_email = models.EmailField()
    price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="active")
    current_period_start = models.DateTimeField(null=True)
    current_period_end = models.DateTimeField(null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    # Trial support
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    # Dunning management
    dunning_attempts = models.IntegerField(default=0)
    last_dunning_at = models.DateTimeField(null=True, blank=True)
    grace_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"
        ordering = ["-created_at"]


class Invoice(models.Model):
    """Invoice record."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="invoices")
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    number = models.CharField(max_length=100, blank=True)
    customer_email = models.EmailField()
    amount = models.IntegerField()  # cents
    currency = models.CharField(max_length=3, default="usd")
    status = models.CharField(max_length=50, choices=[
        ("draft", "Draft"),
        ("open", "Open"),
        ("paid", "Paid"),
        ("void", "Void"),
        ("uncollectible", "Uncollectible"),
    ], default="draft")
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    pdf_url = models.URLField(blank=True)
    line_items = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "invoices"
        ordering = ["-created_at"]


class PlatformPlan(models.Model):
    """AgentBloom platform subscription plans."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    stripe_product_id = models.CharField(max_length=255, blank=True)
    price_monthly = models.IntegerField(default=0)  # cents
    price_yearly = models.IntegerField(default=0)  # cents
    features = models.JSONField(default=dict)  # {max_contacts, max_emails, max_courses, ...}
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "platform_plans"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.name} (${self.price_monthly / 100:.0f}/mo)"


class PlatformSubscription(models.Model):
    """An org's subscription to an AgentBloom platform plan."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.OneToOneField("users.Organization", on_delete=models.CASCADE, related_name="platform_subscription")
    plan = models.ForeignKey(PlatformPlan, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, default="active")
    current_period_end = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_subscriptions"


class UsageTracking(models.Model):
    """Track resource usage for billing / plan limits."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="usage")
    metric = models.CharField(max_length=100)  # contacts, emails_sent, ai_tokens, storage_mb
    period = models.DateField()  # Month start
    count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "usage_tracking"
        unique_together = ("org", "metric", "period")


class TaxRule(models.Model):
    """Tax rules for products — manual tax rules or Stripe Tax integration."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="tax_rules")
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=100)  # Country/State code
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    is_inclusive = models.BooleanField(default=False)  # Tax inclusive in price
    applies_to = models.JSONField(default=list, blank=True)  # Product IDs or "all"
    stripe_tax_rate_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "tax_rules"


class Refund(models.Model):
    """Refund request and processing."""

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("denied", "Denied"),
        ("processed", "Processed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="refunds")
    stripe_refund_id = models.CharField(max_length=255, blank=True)
    amount = models.IntegerField()  # cents
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="requested")
    requested_by_email = models.EmailField(blank=True)
    approved_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "refunds"
        ordering = ["-created_at"]


class OrderBump(models.Model):
    """Order bump / upsell displayed at checkout."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="order_bumps")
    trigger_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bumps_triggered")
    bump_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bump_offers")
    bump_price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True, blank=True)
    headline = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    position = models.CharField(max_length=50, choices=[
        ("checkout", "At Checkout"),
        ("post_purchase", "Post-Purchase"),
    ], default="checkout")
    is_active = models.BooleanField(default=True)
    impressions = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "order_bumps"


class CheckoutPage(models.Model):
    """Branded checkout page (not just Stripe default)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="checkout_pages")
    slug = models.SlugField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="checkout_pages")
    price = models.ForeignKey(Price, on_delete=models.SET_NULL, null=True)
    headline = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_blocks = models.JSONField(default=list, blank=True)  # Custom layout
    thank_you_url = models.URLField(blank=True)
    testimonials = models.JSONField(default=list, blank=True)
    guarantee_text = models.TextField(blank=True)
    timer_enabled = models.BooleanField(default=False)
    timer_minutes = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    conversion_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "checkout_pages"
        unique_together = ("org", "slug")


class RevenueSnapshot(models.Model):
    """Daily revenue snapshot for financial reporting dashboard."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey("users.Organization", on_delete=models.CASCADE, related_name="revenue_snapshots")
    date = models.DateField()
    revenue = models.IntegerField(default=0)  # cents
    refunds = models.IntegerField(default=0)  # cents
    net_revenue = models.IntegerField(default=0)  # cents
    new_subscriptions = models.IntegerField(default=0)
    churned_subscriptions = models.IntegerField(default=0)
    mrr = models.IntegerField(default=0)  # Monthly recurring revenue in cents
    active_subscribers = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "revenue_snapshots"
        unique_together = ("org", "date")
        ordering = ["-date"]
