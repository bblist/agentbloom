# Phase 8 — Knowledge Base

> **Goal**: Build the knowledge base system — upload, process, embed, and search. The KB powers the agent's contextual understanding, content generation, and (eventually) the AI receptionist.

## Status: NOT STARTED

## Dependencies
- Phase 0 (Foundation) — S3, DB with pgvector
- Phase 1 (Agent) — agent uses KB for context

## Checklist

### Upload Pipeline
- [ ] Upload interface: drag-drop zone + file picker
- [ ] Supported formats:
  - [ ] PDF → text extraction (PyPDF2/pdfplumber)
  - [ ] DOCX → text extraction (python-docx)
  - [ ] PPTX → text extraction (python-pptx)
  - [ ] TXT/MD → direct use
  - [ ] CSV → structured extraction
  - [ ] Audio (MP3, WAV, M4A) → transcription (Deepgram/Whisper)
  - [ ] Video (MP4, MOV) → audio extraction → transcription
  - [ ] URL → web scraping (BeautifulSoup/Trafilatura)
- [ ] Upload progress indicator
- [ ] Processing pipeline status per file:
  - [ ] Uploaded → Processing → Extracting Text → Chunking → Embedding → Ready / Error
- [ ] File size limits per plan (e.g., 10MB free, 100MB pro)
- [ ] Async processing (Celery task queue)

### Text Processing
- [ ] Text extraction from all supported formats
- [ ] Text cleaning: remove headers/footers, fix encoding, normalize whitespace
- [ ] Chunking strategy:
  - [ ] Smart chunking: by paragraph/section with overlap (512 tokens per chunk, 64 token overlap)
  - [ ] Preserve document structure (section headings as metadata)
  - [ ] Handle tables: extract as structured data
- [ ] Metadata per chunk: source document, page number, section, creation date

### Vector Embeddings
- [ ] Embedding model: OpenAI text-embedding-3-small (or Gemini embedding)
- [ ] Store in pgvector (PostgreSQL extension)
- [ ] Index: IVFFlat or HNSW for fast approximate search
- [ ] Batch embedding on upload (async)
- [ ] Re-embed on document update

### Semantic Search
- [ ] Search API: query → embed → find top-K similar chunks
- [ ] Hybrid search: semantic (vector) + keyword (full-text) combined scoring
- [ ] Filter by document, date, tags
- [ ] Search UI in dashboard: search across all KB content
- [ ] Relevance scoring and ranking

### Source Management
- [ ] Document list view: name, type, status, size, date, chunk count
- [ ] Document detail: view extracted text, preview chunks
- [ ] Edit extracted text (fix OCR errors, update outdated info)
- [ ] Delete document (cascade delete chunks + embeddings)
- [ ] Archive/unarchive (temporarily exclude from agent context)
- [ ] Tags/categories for organization
- [ ] Freshness indicator: flag old documents (>6 months)

### Auto-FAQ Generation
- [ ] Agent analyzes KB → extracts common questions and answers
- [ ] Generate FAQ page (uses page builder)
- [ ] Generate receptionist scripts (for future Phase 11)
- [ ] Review/edit generated FAQs before publishing

### Website URL Scraper
- [ ] Input: one or multiple URLs
- [ ] Scraping: extract clean text from web pages (Trafilatura)
- [ ] Option: scrape entire site (follow internal links, depth limit)
- [ ] Preview scraped content before adding to KB
- [ ] Schedule re-scraping (keep KB updated with website changes)

### Google Business Profile Import
- [ ] Connect Google Business Profile API
- [ ] Import: business info (NAP), reviews, Q&A
- [ ] Convert reviews to KB chunks (agent can reference in testimonials)
- [ ] Import FAQ from GBP Q&A
- [ ] Sync: periodic refresh

### Agent Integration
- [ ] Context retrieval: agent queries KB before generating content
- [ ] Top-K chunks injected into system prompt (with source attribution)
- [ ] Agent cites sources: "Based on your uploaded document..."
- [ ] Agent can suggest KB improvements: "Your pricing doc is outdated"
- [ ] Agent commands: "search knowledge base for pricing", "add this URL to KB"

### Agent Tools (Phase 8)
- [ ] `search_knowledge_base` — Semantic search across KB
- [ ] `add_to_knowledge_base` — Upload/scrape content
- [ ] `generate_faq` — Create FAQ from KB content
- [ ] `review_kb_health` — Check for stale/conflicting info

### Database Schema (Phase 8 additions)
```sql
CREATE TABLE kb_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    source_type VARCHAR(50) NOT NULL, -- upload, url, gbp
    source_url TEXT, -- for URL/GBP sources
    file_type VARCHAR(50), -- pdf, docx, pptx, txt, audio, video
    file_size BIGINT,
    s3_key TEXT,
    status VARCHAR(50) DEFAULT 'processing', -- processing, ready, error, archived
    error_message TEXT,
    extracted_text TEXT,
    word_count INTEGER,
    chunk_count INTEGER DEFAULT 0,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}', -- page count, duration, etc.
    last_processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE kb_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES kb_documents(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    token_count INTEGER,
    metadata JSONB DEFAULT '{}', -- section_title, page_number, etc.
    embedding vector(1536), -- pgvector: 1536 dims for text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast vector search
CREATE INDEX idx_kb_chunks_embedding ON kb_chunks USING hnsw (embedding vector_cosine_ops);

-- Index for filtering by org
CREATE INDEX idx_kb_chunks_org ON kb_chunks(org_id);

CREATE TABLE kb_scrape_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES kb_documents(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    frequency VARCHAR(50) DEFAULT 'weekly', -- daily, weekly, monthly
    last_scraped_at TIMESTAMPTZ,
    next_scrape_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE gbp_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    google_account_email VARCHAR(255),
    location_id VARCHAR(255),
    business_name VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    last_sync_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Acceptance Criteria
- [ ] User can upload PDF, DOCX, PPTX, TXT, audio, video files
- [ ] Processing pipeline runs asynchronously with status updates
- [ ] Extracted text is viewable and editable
- [ ] Semantic search returns relevant chunks
- [ ] Auto-FAQ generation works from KB content
- [ ] URL scraper extracts and stores web page content
- [ ] Agent uses KB context when generating content
- [ ] Agent cites KB sources in responses
- [ ] Source management (CRUD, archive, tags) works
- [ ] Freshness indicators flag old content

## Known Risks
- Transcription costs: Whisper self-hosted is free but requires GPU. Deepgram/AssemblyAI charge per minute.
- Embedding costs: text-embedding-3-small is cheap (~$0.02/1M tokens) but large KBs add up.
- pgvector performance: Works well up to ~1M vectors. Beyond that, consider Pinecone or Weaviate.
- Web scraping: Some sites block scrapers. Need rate limiting and respectful scraping.

## What's Next
Phase 9 (Admin Panel) — final backend before polish.
