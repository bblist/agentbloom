from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"stripe", views.StripeConnectionViewSet, basename="stripe")
router.register(r"products", views.ProductViewSet, basename="product")
router.register(r"prices", views.PriceViewSet, basename="price")
router.register(r"coupons", views.CouponViewSet, basename="coupon")
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"subscriptions", views.SubscriptionViewSet, basename="subscription")
router.register(r"invoices", views.InvoiceViewSet, basename="invoice")
router.register(r"refunds", views.RefundViewSet, basename="refund")
router.register(r"tax-rules", views.TaxRuleViewSet, basename="tax-rule")
router.register(r"order-bumps", views.OrderBumpViewSet, basename="order-bump")
router.register(r"checkout-pages", views.CheckoutPageViewSet, basename="checkout-page")
router.register(r"plans", views.PlatformPlanViewSet, basename="plan")
router.register(r"platform-subscription", views.PlatformSubscriptionViewSet, basename="platform-subscription")
router.register(r"usage", views.UsageTrackingViewSet, basename="usage")
router.register(r"revenue", views.RevenueSnapshotViewSet, basename="revenue")

urlpatterns = [
    path("", include(router.urls)),
]
