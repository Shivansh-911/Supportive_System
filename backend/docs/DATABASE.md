# Database — Publive CX AI Support System

## Engine

Postgres with pgvector extension.
Single database, single instance for Phase 1.

---

## Tables

### document_store
Source of truth for all ingested documents. One row per source document. This is the parent record — child chunks reference this table via doc_id.

- `doc_id` — UUID primary key
- `sync_event_id` — FK to sync_events, references the most recent sync_event that triggered this document's ingest; updated on every re-ingest
- `source_type` — `freshdesk_article` | `freshdesk_ticket` | `notion_page` | `loom_video`
- `source_id` — String
- `source_url` — source URL, surfaced in citations
- `source_title` — source title
- `source_created_at`, `source_updated_at` — timestamps from payload
- `source_author` — JSONB; `{ "name": "..." }` for articles/pages/videos, `{ "requester": "...", "assignee": "..." }` for tickets
- `source_metadata` — JSONB, source-specific fields; shape varies by source_type:
    - freshdesk_article: `{ "category_id", "folder_id", "tags": [], "article_status": "published|draft" }`
    - freshdesk_ticket: `{ "ticket_number", "priority": "low|medium|high|urgent", "ticket_status": "open|pending|resolved|closed", "tags": [] }`
    - loom_video: `{ "duration_seconds", "thumbnail_url" }`
    - notion_page: `{ "database_id", "page_properties": {}, "tags": [] }`
- `structured_json` — JSONB, structured json content used by chunker
- `cleaned_html` — cleaned html after parsing; null for sources with no HTML (e.g. loom_video)
- `cleaned_text` — plain text of full document, sent to LLM as context at retrieval time
- `content_hash` — SHA-256 of cleaned_text, used to skip unchanged documents on re-ingest
- `first_ingested_at` — never updated after initial insert
- `last_ingested_at` — updated on every re-ingest
- `word_count` — total no of words
- `chunk_count` — total no of chunks in document
- `status` — active | retired
- `retired_at` — timestamp when status was set to retired, nullable

Unique Constraint on (source_id , source_type)

---

### sync_events
Pipeline control table. Tracks every source event from entry through to ingestion completion. Never deleted — permanent audit trail.

- `event_id` — UUID primary key
- `source_id` — Source ID from source event
- `source_type` — `freshdesk_article` | `freshdesk_ticket` | `notion_page` | `loom_video`
- `source_title` — Source title from source event
- `source_url` — source URL
- `event_type` — `created` | `updated` | `deleted`
- `source_created_at`, `source_updated_at` — from source event
- `detected_at` — when the server received the webhook POST
- `source_payload` — JSONB, raw event data from source worker (webhook body, poll response, or manual trigger); passed to process agent at dispatch time, avoids re-fetching from source API
- `status` — pending | approved | rejected | processing | completed | failed
- `actioned_by`, `actioned_at` — who approved or rejected and when
- `processing_started_at`, `processing_completed_at` — pipeline timing
- `retry_count` — int, default 0; incremented by outbox worker on each failed dispatch
- `next_retry_at` — timestamp, nullable; set by outbox worker for exponential backoff; null means not scheduled for retry
- `error_stage` — which pipeline step failed (e.g. `cleaning`, `chunking`, `embedding`), nullable
- `error_message` — human-readable failure detail, surfaced in ops UI for re-trigger
- `UNIQUE (source_id, source_type, source_updated_at)` — idempotency guard, duplicate webhook events silently dropped

**Status lifecycle:** pending → approved → processing → completed / failed

**Concurrency:** outbox worker must claim events using `SELECT FOR UPDATE SKIP LOCKED` to prevent double-processing when multiple workers run.

---

### chunks
Embedding units. One row per chunk per document. Deleted and replaced on every re-ingest of the parent document.

- `chunk_id` — UUID primary key
- `doc_id` — FK to document_store, ON DELETE CASCADE
- `source_type` — from document_store, enables filtered retrieval without a join
- `source_id` — from document_store, String ID from the originating source
- `source_url` — from document_store, source_url;
- `position` — chunk order within the document
- `content` — clean body text, used for citation and display
- `searchable_text` — context prefix + body text, what gets embedded and what the reranker scores; shape varies by source_type:
  - freshdesk_article: `[category name] > [folder name] > [article_title] > [body]`
- `embedding` — vector(512), voyage-3-lite, cosine distance, HNSW indexed
- `model_id` — which embedding model was used to produce the embedding
- `content_tsv` — generated tsvector from searchable_text, powers sparse retrieval, GIN indexed
- `token_count` — token count of searchable_text, used to monitor chunk size distribution
- `chunk_strategy` — `heading_aware` | `recursive_fallback` 
  - `heading_aware` — freshdesk_article, notion_page with heading structure
  - `recursive_fallback` — any document without heading structure
- `context_prefix` — string | null, LLM-generated 1–2 sentence context description prepended to searchable_text; null only if context generation failed (error logged)
- `metadata` — JSONB, additional pipeline-level fields; shape varies by source_type:
  - freshdesk_article / notion_page: `{ "heading_path": ["H1", "H2"], "is_table": bool, "is_code_block": bool }`
  - freshdesk_ticket: `{ "turn_index": int, "author_role": "customer|agent", "message_id": "..." }`
  - loom_video: `{ "start_time_seconds": int, "end_time_seconds": int }`
- `created_at` — timestamp of chunk creation

**Indexes** — HNSW on embedding (cosine), GIN on content_tsv, btree on doc_id, btree on source_type.

**ON DELETE CASCADE** — deleting a document_store row automatically removes all its chunks.

**UNIQUE (doc_id, position)** — idempotency guard, prevents duplicate chunks on re-ingest.

---

## Migration Files

Numbered SQL files in `src/db/migrations/`:

```
001_create_sync_events.sql
002_create_document_store.sql
003_create_chunks.sql
```
