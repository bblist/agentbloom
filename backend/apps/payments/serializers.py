from rest_framework import serializers
from .models import (
    StripeConnection, Product, Price, Coupon, Payment, Subscription,
    Invoice, PlatformPlan, PlatformSubscription, UsageTracking,
    TaxRule, Refund, OrderBump, CheckoutPage, RevenueSnapshot,
)


class StripeConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeConnection
        fields = "__all__"
        read_only_fields = (
            "id", "org", "stripe_account_id", "charges_enabled",
            "payouts_enabled", "details_submitted", "onboarding_complete",
            "created_at", "updated_at",
        )


class PriceSerializer(serializers.ModelSerializer):
    display_amount = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def get_display_amount(self, obj):
        return f"${obj.amount / 100:.2f}"


class ProductSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "org", "stripe_product_id", "created_at", "updated_at")


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"
        read_only_fields = ("id", "org", "times_redeemed", "stripe_coupon_id", "created_at")


class PaymentSerializer(serializers.ModelSerializer):
    display_amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = (
            "id", "org", "stripe_payment_intent_id",
            "refunded_amount", "created_at", "updated_at",
        )

    def get_display_amount(self, obj):
        return f"${obj.amount / 100:.2f}"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = (
            "id", "org", "stripe_subscription_id",
            "dunning_attempts", "last_dunning_at",
            "created_at", "updated_at",
        )


class InvoiceSerializer(serializers.ModelSerializer):
    display_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("id", "org", "stripe_invoice_id", "created_at")

    def get_display_amount(self, obj):
        return f"${obj.amount / 100:.2f}"


class PlatformPlanSerializer(serializers.ModelSerializer):
    display_monthly = serializers.SerializerMethodField()

    class Meta:
        model = PlatformPlan
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def get_display_monthly(self, obj):
        return f"${obj.price_monthly / 100:.2f}"


class PlatformSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = PlatformSubscription
        fields = "__all__"
        read_only_fields = ("id", "org", "stripe_subscription_id", "created_at", "updated_at")


class UsageTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageTracking
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at", "updated_at")


class TaxRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRule
        fields = "__all__"
        read_only_fields = ("id", "org", "stripe_tax_rate_id", "created_at")


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"
        read_only_fields = ("id", "stripe_refund_id", "processed_at", "created_at")


class OrderBumpSerializer(serializers.ModelSerializer):
    conversion_rate = serializers.SerializerMethodField()

    class Meta:
        model = OrderBump
        fields = "__all__"
        read_only_fields = ("id", "org", "impressions", "conversions", "created_at")

    def get_conversion_rate(self, obj):
        if obj.impressions == 0:
            return 0
        return round(obj.conversions / obj.impressions * 100, 1)


class CheckoutPageSerializer(serializers.ModelSerializer):
    conversion_rate = serializers.SerializerMethodField()

    class Meta:
        model = CheckoutPage
        fields = "__all__"
        read_only_fields = (
            "id", "org", "view_count", "conversion_count",
            "created_at", "updated_at",
        )

    def get_conversion_rate(self, obj):
        if obj.view_count == 0:
            return 0
        return round(obj.conversion_count / obj.view_count * 100, 1)


class RevenueSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueSnapshot
        fields = "__all__"
        read_only_fields = ("id", "org", "created_at")


class CouponValidateSerializer(serializers.Serializer):
    """Input for coupon validation."""
    code = serializers.CharField()
    product_id = serializers.UUIDField(required=False)
    amount = serializers.IntegerField(required=False, help_text="Cart amount in cents")
