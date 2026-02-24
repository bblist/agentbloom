"""Celery tasks for webhook delivery."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def deliver_webhook(self, endpoint_id, event_id):
    """Deliver a webhook event to an endpoint with retries."""
    import httpx
    import hashlib
    import hmac
    import json
    import time
    from .models import WebhookEndpoint, WebhookEvent, WebhookDeliveryLog

    try:
        endpoint = WebhookEndpoint.objects.get(id=endpoint_id)
        event = WebhookEvent.objects.get(id=event_id)

        payload = json.dumps({
            "event": event.event_type,
            "data": event.payload,
            "timestamp": event.created_at.isoformat(),
            "webhook_id": str(event.id),
        })

        # Sign payload
        signature = hmac.new(
            endpoint.secret.encode() if endpoint.secret else b"",
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Event": event.event_type,
            "User-Agent": "AgentBloom-Webhooks/1.0",
        }

        start = time.time()
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(endpoint.url, content=payload, headers=headers)

            elapsed = int((time.time() - start) * 1000)

            WebhookDeliveryLog.objects.create(
                endpoint=endpoint,
                event=event,
                status_code=response.status_code,
                response_body=response.text[:5000],
                response_time_ms=elapsed,
                success=200 <= response.status_code < 300,
                attempt=self.request.retries + 1,
            )

            if not (200 <= response.status_code < 300):
                raise Exception(f"Webhook returned {response.status_code}")

            return {"status": "delivered", "status_code": response.status_code}

        except httpx.RequestError as e:
            elapsed = int((time.time() - start) * 1000)
            WebhookDeliveryLog.objects.create(
                endpoint=endpoint,
                event=event,
                status_code=0,
                response_body=str(e),
                response_time_ms=elapsed,
                success=False,
                attempt=self.request.retries + 1,
            )
            raise

    except Exception as exc:
        retry_delay = 60 * (2 ** self.request.retries)  # Exponential backoff
        logger.error(f"Webhook delivery failed (attempt {self.request.retries + 1}): {exc}")
        self.retry(exc=exc, countdown=retry_delay)


@shared_task
def process_incoming_webhook(webhook_id):
    """Process a received incoming webhook."""
    from .models import IncomingWebhook

    try:
        webhook = IncomingWebhook.objects.get(id=webhook_id)
        source = webhook.source
        payload = webhook.payload

        # Route based on source
        if source == "stripe":
            # Handle Stripe webhook events
            event_type = payload.get("type", "")
            logger.info(f"Processing Stripe webhook: {event_type}")
            # TODO: Route to payments app
        elif source == "ses":
            # Handle SES notification (bounces, complaints)
            from apps.email_crm.tasks import process_email_event
            process_email_event.delay(payload)
        elif source == "google":
            logger.info("Processing Google webhook")
            # TODO: Route to calendar/GBP

        webhook.status = "processed"
        webhook.save(update_fields=["status"])

        return {"status": "processed", "source": source}

    except IncomingWebhook.DoesNotExist:
        logger.error(f"IncomingWebhook {webhook_id} not found")
        return {"error": "not_found"}
