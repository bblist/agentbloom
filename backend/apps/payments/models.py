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
