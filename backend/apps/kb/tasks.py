"""Celery tasks for KB processing."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def process_kb_document(self, document_id):
    """Process a KB document: extract text → chunk → embed."""
    from .models import KBDocument, KBChunk

    try:
        doc = KBDocument.objects.get(id=document_id)
        doc.status = "processing"
        doc.processing_step = "extracting"
        doc.processing_progress = 10
        doc.save(update_fields=["status", "processing_step", "processing_progress"])

        # Step 1: Extract text
        text = doc.raw_text or doc.extracted_text
        if not text and doc.source_type == "url" and doc.source_url:
            # Scrape URL
            import httpx
            try:
                resp = httpx.get(doc.source_url, follow_redirects=True, timeout=30)
                from html.parser import HTMLParser
                import re

                class TextExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.text_parts = []
                        self.skip = False

                    def handle_starttag(self, tag, attrs):
                        if tag in ("script", "style", "nav", "footer"):
                            self.skip = True

                    def handle_endtag(self, tag):
                        if tag in ("script", "style", "nav", "footer"):
                            self.skip = False

                    def handle_data(self, data):
                        if not self.skip:
                            self.text_parts.append(data.strip())

                parser = TextExtractor()
                parser.feed(resp.text)
                text = "\n".join(p for p in parser.text_parts if p)
                text = re.sub(r"\n{3,}", "\n\n", text)
            except Exception as e:
                doc.status = "failed"
                doc.error_message = f"URL scrape failed: {e}"
                doc.save(update_fields=["status", "error_message"])
                return {"error": str(e)}

        if not text:
            doc.status = "failed"
            doc.error_message = "No text content to process"
            doc.save(update_fields=["status", "error_message"])
            return {"error": "no_text"}

        doc.extracted_text = text
        doc.processing_step = "chunking"
        doc.processing_progress = 40
        doc.save(update_fields=["extracted_text", "processing_step", "processing_progress"])

        # Step 2: Chunk text
        chunks = chunk_text(text, chunk_size=500, overlap=50)

        # Delete old chunks
        doc.chunks.all().delete()

        doc.processing_step = "embedding"
        doc.processing_progress = 60
        doc.save(update_fields=["processing_step", "processing_progress"])

        # Step 3: Create chunks (embeddings added later when OpenAI key available)
        for i, chunk_text_content in enumerate(chunks):
            KBChunk.objects.create(
                document=doc,
                content=chunk_text_content,
                chunk_index=i,
                token_count=len(chunk_text_content.split()),
            )

        doc.chunk_count = len(chunks)
        doc.status = "completed"
        doc.processing_step = "done"
        doc.processing_progress = 100
        doc.error_message = ""
        doc.save(update_fields=[
            "chunk_count", "status", "processing_step",
            "processing_progress", "error_message",
        ])

        logger.info(f"Processed KB doc '{doc.title}': {len(chunks)} chunks")
        return {"document_id": str(document_id), "chunks": len(chunks)}

    except KBDocument.DoesNotExist:
        logger.error(f"KBDocument {document_id} not found")
        return {"error": "not_found"}
    except Exception as exc:
        logger.error(f"KB processing failed: {exc}")
        try:
            doc = KBDocument.objects.get(id=document_id)
            doc.status = "failed"
            doc.error_message = str(exc)
            doc.save(update_fields=["status", "error_message"])
        except Exception:
            pass
        self.retry(exc=exc, countdown=60)


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


@shared_task
def embed_chunks(document_id):
    """Generate embeddings for all chunks of a document."""
    from .models import KBDocument, KBChunk
    import os

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("No OPENAI_API_KEY — skipping embeddings")
        return {"error": "no_api_key"}

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        doc = KBDocument.objects.get(id=document_id)
        chunks = doc.chunks.filter(embedding__isnull=True)

        for chunk in chunks:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk.content,
            )
            chunk.embedding = response.data[0].embedding
            chunk.save(update_fields=["embedding"])

        logger.info(f"Embedded {chunks.count()} chunks for doc '{doc.title}'")
        return {"embedded": chunks.count()}

    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return {"error": str(e)}


@shared_task
def scrape_scheduled_urls():
    """Run all due scrape schedules."""
    from django.utils import timezone
    from .models import KBScrapeSchedule, KBDocument

    now = timezone.now()
    due = KBScrapeSchedule.objects.filter(
        is_active=True,
        next_scrape__lte=now,
    )

    for schedule in due:
        # Create or update document
        doc, _ = KBDocument.objects.update_or_create(
            org=schedule.org,
            source_url=schedule.url,
            source_type="url",
            defaults={
                "title": f"Scrape: {schedule.url}",
                "status": "pending",
            },
        )
        process_kb_document.delay(str(doc.id))

        # Update next scrape time
        from datetime import timedelta
        if schedule.frequency == "daily":
            schedule.next_scrape = now + timedelta(days=1)
        elif schedule.frequency == "weekly":
            schedule.next_scrape = now + timedelta(weeks=1)
        else:
            schedule.next_scrape = now + timedelta(days=30)
        schedule.last_scraped = now
        schedule.save(update_fields=["next_scrape", "last_scraped"])

    return {"scheduled_scrapes": due.count()}
