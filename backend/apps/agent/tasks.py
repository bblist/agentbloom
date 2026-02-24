"""Celery tasks for agent operations."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def run_agent_async(self, org_id, user_id, conversation_id, message_content):
    """Run agent processing asynchronously (for non-streaming requests)."""
    try:
        import asyncio
        from .engine import run_agent, AgentContext
        from .models import AgentConfig, Conversation, Message
        from apps.users.models import Organization

        org = Organization.objects.get(id=org_id)
        config = AgentConfig.objects.get(org=org)
        conversation = Conversation.objects.get(id=conversation_id)

        # Build context
        context = AgentContext(
            org_id=str(org.id),
            user_id=str(user_id),
            conversation_id=str(conversation.id),
            agent_config={
                "provider": config.llm_provider,
                "model": config.llm_model,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "persona": config.persona,
                "tone": config.tone,
            },
        )

        # Get conversation messages
        messages = Message.objects.filter(
            conversation=conversation
        ).order_by("created_at")
        history = []
        for m in messages:
            history.append({"role": m.role, "content": m.content})

        # Run agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_agent(context, history))
        finally:
            loop.close()

        # Save assistant message
        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=result.content,
            token_count=result.total_tokens,
            model_used=result.model_used,
            latency_ms=result.latency_ms,
        )

        return {
            "status": "completed",
            "content": result.content,
            "tokens": result.total_tokens,
        }

    except Exception as exc:
        logger.error(f"Agent async task failed: {exc}")
        self.retry(exc=exc, countdown=5)


@shared_task
def cleanup_old_conversations(days=90):
    """Delete conversations older than N days with no messages in that period."""
    from django.utils import timezone
    from datetime import timedelta
    from .models import Conversation

    cutoff = timezone.now() - timedelta(days=days)
    old = Conversation.objects.filter(updated_at__lt=cutoff)
    count = old.count()
    old.delete()
    logger.info(f"Cleaned up {count} old conversations (>{days} days)")
    return {"deleted": count}


@shared_task
def run_scheduled_tasks():
    """Execute scheduled agent tasks that are due."""
    from django.utils import timezone
    from .models import ScheduledTask

    now = timezone.now()
    tasks = ScheduledTask.objects.filter(
        is_active=True,
        next_run__lte=now,
    )

    for task in tasks:
        try:
            run_agent_async.delay(
                str(task.org_id), str(task.created_by_id),
                None, task.task_config.get("prompt", ""),
            )
            # Update next run based on frequency
            if task.frequency == "daily":
                task.next_run = now + timezone.timedelta(days=1)
            elif task.frequency == "weekly":
                task.next_run = now + timezone.timedelta(weeks=1)
            elif task.frequency == "monthly":
                task.next_run = now + timezone.timedelta(days=30)
            task.last_run = now
            task.save(update_fields=["next_run", "last_run"])
        except Exception as e:
            logger.error(f"Scheduled task {task.id} failed: {e}")

    return {"executed": tasks.count()}
