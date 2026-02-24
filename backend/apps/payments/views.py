from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone

from .models import (
    StripeConnection, Product, Price, Coupon, Payment, Subscription,
    Invoice, PlatformPlan, PlatformSubscription, UsageTracking,
    TaxRule, Refund, OrderBump, CheckoutPage, RevenueSnapshot,
)
from .serializers import (
    StripeConnectionSerializer, ProductSerializer, PriceSerializer,
    CouponSerializer, PaymentSerializer, SubscriptionSerializer,
    InvoiceSerializer, PlatformPlanSerializer, PlatformSubscriptionSerializer,
    UsageTrackingSerializer, TaxRuleSerializer, RefundSerializer,
    OrderBumpSerializer, CheckoutPageSerializer, RevenueSnapshotSerializer,
    CouponValidateSerializer,
)


class StripeConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = StripeConnectionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head"]

    def get_queryset(self):
        return StripeConnection.objects.filter(org=self.request.org)

    @action(detail=False, methods=["post"])
    def onboard(self, request):
        """Initiate Stripe Connect onboarding. Returns onboarding URL."""
        import stripe
        from django.conf import settings as conf

        stripe.api_key = conf.STRIPE_SECRET_KEY
        if not stripe.api_key:
            return Response(
                {"error": "Stripe is not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Check for existing connection
        conn = StripeConnection.objects.filter(org=request.org).first()
        if conn and conn.stripe_account_id:
            account_id = conn.stripe_account_id
        else:
            # Create a new Express account
            account = stripe.Account.create(
                type="express",
                email=request.user.email,
                metadata={"org_id": str(request.org.id)},
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
            )
            account_id = account.id
            conn, _ = StripeConnection.objects.update_or_create(
                org=request.org,
                defaults={
                    "stripe_account_id": account_id,
                    "status": "pending",
                },
            )

        # Create an account link for onboarding
        refresh_url = f"{conf.FRONTEND_URL}/dashboard/payments?stripe=refresh"
        return_url = f"{conf.FRONTEND_URL}/dashboard/payments?stripe=complete"

        link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        return Response({
            "onboarding_url": link.url,
            "account_id": account_id,
        })

    @action(detail=False, methods=["get"])
    def status(self, request):
        """Check current Stripe connection status."""
        try:
            conn = StripeConnection.objects.get(org=request.org)
            return Response(StripeConnectionSerializer(conn).data)
        except StripeConnection.DoesNotExist:
            return Response({"connected": False})


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(org=self.request.org).prefetch_related("prices")

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class PriceViewSet(viewsets.ModelViewSet):
    serializer_class = PriceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Price.objects.filter(product__org=self.request.org)


class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Coupon.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=False, methods=["post"])
    def validate(self, request):
        """Validate a coupon code and return discount details."""
        ser = CouponValidateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        code = ser.validated_data["code"]
        try:
            coupon = Coupon.objects.get(
                org=request.org, code=code, is_active=True,
            )
        except Coupon.DoesNotExist:
            return Response({"valid": False, "error": "Invalid coupon code"}, status=404)

        now = timezone.now()
        if coupon.valid_until and coupon.valid_until < now:
            return Response({"valid": False, "error": "Coupon expired"})
        if coupon.max_redemptions > 0 and coupon.times_redeemed >= coupon.max_redemptions:
            return Response({"valid": False, "error": "Coupon fully redeemed"})

        return Response({
            "valid": True,
            "discount_type": coupon.discount_type,
            "discount_value": float(coupon.discount_value),
            "code": coupon.code,
        })


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head"]

    def get_queryset(self):
        qs = Payment.objects.filter(org=self.request.org)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Revenue summary for the org."""
        payments = Payment.objects.filter(org=request.org, status="succeeded")
        total = sum(p.amount for p in payments)
        return Response({
            "total_revenue_cents": total,
            "total_revenue": f"${total / 100:.2f}",
            "payment_count": payments.count(),
        })


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Subscription.objects.filter(org=self.request.org)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        sub = self.get_object()
        sub.cancel_at_period_end = True
        sub.cancelled_at = timezone.now()
        sub.save(update_fields=["cancel_at_period_end", "cancelled_at", "updated_at"])
        return Response({"status": "cancel_at_period_end"})


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)

    @action(detail=True, methods=["post"])
    def send_invoice(self, request, pk=None):
        """Send invoice to customer via email."""
        invoice = self.get_object()
        if invoice.status == "draft":
            invoice.status = "open"
            invoice.save(update_fields=["status"])

        from django.core.mail import send_mail as _send_mail
        from django.conf import settings as conf
        _send_mail(
            subject=f"Invoice #{invoice.invoice_number} from {invoice.org.name}",
            message=(
                f"You have a new invoice.\n\n"
                f"Amount Due: ${invoice.total_amount}\n"
                f"Due Date: {invoice.due_date}\n\n"
                f"Thank you for your business!"
            ),
            from_email=conf.DEFAULT_FROM_EMAIL,
            recipient_list=[invoice.customer_email],
            fail_silently=True,
        )
        return Response({"status": invoice.status, "sent": True})

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = "paid"
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=["status", "paid_at"])
        return Response({"status": "paid"})


class RefundViewSet(viewsets.ModelViewSet):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Refund.objects.filter(payment__org=self.request.org)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        refund = self.get_object()
        import stripe
        from django.conf import settings as conf

        stripe.api_key = conf.STRIPE_SECRET_KEY
        payment = refund.payment

        try:
            if stripe.api_key and payment.stripe_charge_id:
                stripe.Refund.create(
                    charge=payment.stripe_charge_id,
                    amount=int(refund.amount * 100),  # cents
                    reason=refund.reason or "requested_by_customer",
                )
        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Stripe refund failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        refund.status = "approved"
        refund.approved_by = request.user
        refund.save(update_fields=["status", "approved_by"])

        payment.status = "refunded"
        payment.save(update_fields=["status"])

        return Response({"status": "approved"})


class TaxRuleViewSet(viewsets.ModelViewSet):
    serializer_class = TaxRuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaxRule.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class OrderBumpViewSet(viewsets.ModelViewSet):
    serializer_class = OrderBumpSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderBump.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class CheckoutPageViewSet(viewsets.ModelViewSet):
    serializer_class = CheckoutPageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CheckoutPage.objects.filter(org=self.request.org)

    def perform_create(self, serializer):
        serializer.save(org=self.request.org)


class PlatformPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Public: list available platform plans."""
    serializer_class = PlatformPlanSerializer
    permission_classes = [AllowAny]
    queryset = PlatformPlan.objects.filter(is_active=True)


class PlatformSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PlatformSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "head"]

    def get_queryset(self):
        return PlatformSubscription.objects.filter(org=self.request.org)

    @action(detail=False, methods=["post"])
    def upgrade(self, request):
        """Upgrade/change platform plan."""
        plan_id = request.data.get("plan_id")
        if not plan_id:
            return Response({"error": "plan_id required"}, status=400)
        try:
            plan = PlatformPlan.objects.get(id=plan_id, is_active=True)
        except PlatformPlan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=404)

        sub, created = PlatformSubscription.objects.update_or_create(
            org=request.org,
            defaults={"plan": plan, "status": "active"},
        )
        return Response(PlatformSubscriptionSerializer(sub).data)


class UsageTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UsageTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UsageTracking.objects.filter(org=self.request.org)


class RevenueSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RevenueSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RevenueSnapshot.objects.filter(org=self.request.org)
