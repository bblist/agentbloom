from django.contrib import admin
from .models import (
    StripeConnection, Product, Price, Coupon, Payment,
    Subscription, Invoice, PlatformPlan, PlatformSubscription,
)


@admin.register(StripeConnection)
class StripeConnectionAdmin(admin.ModelAdmin):
    list_display = ("org", "stripe_account_id", "charges_enabled", "payouts_enabled")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "org", "stripe_product_id", "is_active")


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("product", "amount", "currency", "billing_period", "is_active")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "org", "discount_type", "discount_value", "times_redeemed", "is_active")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("org", "amount", "currency", "status", "customer_email", "created_at")
    list_filter = ("status",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("org", "customer_email", "status", "current_period_end")
    list_filter = ("status",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "org", "amount", "status", "due_date")
    list_filter = ("status",)


@admin.register(PlatformPlan)
class PlatformPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_monthly", "price_yearly", "is_active", "sort_order")


@admin.register(PlatformSubscription)
class PlatformSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("org", "plan", "status", "current_period_end")
