# File Structure

## 3-Layer Architecture

```
Layer 1 — Presentation   →   views.py · serializers.py · urls.py
Layer 2 — Business Logic →   services/
Layer 3 — Data Access    →   models/ · managers/ · migrations/
```

Rule: Views call Services. Services call Managers. Nothing skips a layer.

---

```
project_root/
│
├── manage.py                              # Django entry point — sets DJANGO_SETTINGS_MODULE to core.settings (env file chosen by DJANGO_ENV)
├── constants.py                           # All magic values: model names, dimensions, thresholds, provider keys
├── requirements.txt
├── docker-compose.yml
│
│
├── core/                                  # Django project package + shared data-layer app
│   ├── __init__.py
│   ├── apps.py                            # CoreConfig — registers core as an app so its models are discovered
│   ├── asgi.py                            # ASGI entry — points at core.settings
│   ├── wsgi.py                            # WSGI entry — points at core.settings
│   ├── urls.py                            # Root URL conf (currently empty — add urlpatterns when needed)
│   │
│   ├── settings.py                        # Single settings module — loads .env.{DJANGO_ENV} (development | beta | production)
│   │
│   │   # ── Layer 3: Data Access ───────────────────────────────────
│   ├── models/
│   │   ├── __init__.py                    # Re-exports Chunk, Document, SyncEvent + every enum
│   │   ├── chunk.py                       # Chunk model (HNSW vector + tsvector indexes)
│   │   ├── document.py                    # Document model — parent record for chunks
│   │   ├── sync_event.py                  # SyncEvent — pipeline control + audit table
│   │   └── constants/
│   │       ├── __init__.py                # Re-exports the five enums below
│   │       ├── chunk_strategy.py          # ChunkStrategy (heading_aware / recursive_fallback)
│   │       ├── document_status.py         # DocumentStatus (active / retired)
│   │       ├── event_type.py              # EventType (created / updated / deleted)
│   │       ├── source_type.py             # SourceType (freshdesk, freshdesk_ticket, notion_page, loom_video)
│   │       └── sync_event_status.py       # SyncEventStatus (pending / approved / rejected / processing / completed / failed)
│   │
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── chunk_manager.py               # delete_chunks_for_document, bulk_insert_chunks
│   │   ├── document_manager.py            # get_existing_hash, get_active_document, retire_document, insert_document
│   │   └── sync_event_manager.py          # mark_processing, mark_skipped
│   │
│   ├── migrations/
│   │   └── __init__.py                    # Generated migrations land here once makemigrations is run
│   │
│   │   # ── Layer 2: Business Logic (shared infra) ─────────────────
│   └── services/
│       ├── __init__.py
│       ├── adapters/                      # Swappable provider adapters — LLM + embedding
│       │   ├── __init__.py
│       │   ├── embedding/
│       │   │   ├── __init__.py
│       │   │   ├── base.py                # BaseEmbeddingProvider: build(model_id, dimensions) → Embeddings
│       │   │   ├── registry.py            # EmbeddingRegistry — lazy-loads provider by key
│       │   │   └── providers/
│       │   │       ├── __init__.py
│       │   │       └── openai.py          # OpenAI embeddings (text-embedding-3-small, current default)
│       │   └── llm/
│       │       ├── __init__.py
│       │       ├── base.py                # BaseLLMProvider: build(model_id) → BaseChatModel
│       │       ├── registry.py            # LLMRegistry — lazy-loads provider by key
│       │       └── providers/
│       │           ├── __init__.py
│       │           ├── anthropic.py       # ChatAnthropic
│       │           └── openai.py          # ChatOpenAI
│       └── utils/
│           ├── __init__.py
│           └── logger.py                  # get_logger(name) → logging.Logger
│
│
├── process_agent/                          # Ingestion pipeline Django app
│   ├── __init__.py
│   ├── apps.py                             # ProcessAgentConfig
│   │
│   │   # ── Layer 1: Presentation ──────────────────────────────────
│   ├── urls.py
│   ├── views.py
│   ├── serializers.py
│   │
│   │   # ── Layer 2: Business Logic ────────────────────────────────
│   └── services/
│       ├── __init__.py
│       │
│       ├── chunking_strategies/            # Token-aware chunkers
│       │   ├── __init__.py
│       │   ├── heading_aware.py            # MarkdownHeaderTextSplitter + small-section merging; falls back to recursive
│       │   └── recursive.py                # RecursiveCharacterTextSplitter with sentence-aware separators
│       │
│       ├── ingestion_pipelines/            # Source-specific ingestion implementations
│       │   ├── __init__.py
│       │   ├── base_ingestion.py           # BaseIngestion ABC: ingest(event) -> None
│       │   ├── ingestion_factory.py        # build_ingestion(source_type) — registry of pipelines
│       │   ├── freshdesk_helpdocs_ingestion.py    # Freshdesk orchestrator: hash → clean → markdown → chunk → embed → persist
│       │   └── freshdesk_helpdocs/
│       │       ├── __init__.py
│       │       ├── freshdesk_helper.py             # hash, metadata extraction, image link replacement
│       │       ├── freshdesk_cleaner.py            # HTML cleaner (strip data attrs, promote bold paragraphs to h2, etc.)
│       │       ├── freshdesk_structurer.py         # Sections-with-headings builder (currently unused by the main pipeline)
│       │       ├── freshdesk_convet_to_markdown.py # html2text wrapper, detects heading presence
│       │       ├── freshdesk_chunk_helper.py       # build_chunk_image_map, build_chunk_metadata, build_searchable_chunk
│       │       └── freshdesk_context_retrieval.py  # LLM-driven per-chunk context prefix (Freshdesk-tuned prompt)
│       │
│       └── llm/                            # LLM-using pipeline components (not provider adapters)
│           ├── __init__.py
│           └── prefix_generator.py         # Generic context prefix generator (sync + async)
│
│
│
├── question_agent/
│   ├── apps.py
│   ├── urls.py                              # debug-only HTTP surface
│   ├── views.py                             # debug-only — calls the graph directly
│   │
│   ├── graphs/                              # PUBLIC API — orchestrator imports from here
│   │   └── question_graph.py                # build_question_graph() + module-level `question_graph`
│   │
│   ├── states/                              # PUBLIC contract — orchestrator passes / reads this
│   │   ├── question_agent_state.py          # QuestionAgentState (Pydantic BaseModel) — full graph state
│   │   ├── chunk_hit.py                     # ChunkHit — value object for retrieval / rerank results
│   │   └── answer_source.py                 # AnswerSource — enriched cited chunk returned with the answer
│   │
│   ├── nodes/                               # thin state-adapters: state -> service call -> state delta
│   │   ├── scope_check.py
│   │   ├── embed_query.py
│   │   ├── vector_search.py                 # parallel branch — needs query_vector
│   │   ├── bm25_search.py                   # parallel branch — needs only question text
│   │   ├── rrf_fusion.py                    # fans vector_search + bm25_search back in
│   │   ├── reranking.py
│   │   ├── llm_generation.py
│   │   └── metadata_enrichment.py
│   │
│   └── services/                            # business logic — testable without LangGraph
│       ├── prompts/
│       │   ├── scope_check_prompt.py
│       │   └── answer_prompt.py
│       ├── embedding_service.py             # wraps core.services.adapters.embedding
│       ├── retrieval_service.py             # vector_search + bm25_search via chunk_manager
│       ├── rrf_service.py                   # Reciprocal Rank Fusion helper (called by rrf_fusion node)
│       ├── reranking_service.py             # cross-encoder rerank
│       └── generation_service.py            # final LLM call + citation assembly
│
│
│
│
│
├── agents/                                 # LangGraph orchestrators app
│   ├── __init__.py
│   ├── apps.py                             # AgentsConfig
│   │
│   │   # ── Layer 1: Presentation ──────────────────────────────────
│   ├── urls.py
│   ├── views.py
│   ├── serializers.py
│   │
│   │   # ── Layer 2: Business Logic ────────────────────────────────
│   └── services/
│       ├── __init__.py
│       └── process_agent.py                # LangGraph graph — drives pipeline steps in order (placeholder)
│
│
├── docs/
│   ├── CONVENTIONS.md
│   ├── DATABASE.md
│   ├── DECISIONS.md
│   ├── FILE_STRUCTURE.md
│   ├── FUTUTRE_FLAGS.md
│   └── PROCESS_AGENT.md
│
└── tests/                                  # Standalone test scripts (not yet wired into manage.py test)
```

---

## Import path map

| To import from              | Use                                                                |
|-----------------------------|--------------------------------------------------------------------|
| Models                      | `core.models.{chunk,document,sync_event}`                          |
| Model enums                 | `core.models.constants.{source_type,document_status,...}`          |
| Managers                    | `core.managers.{chunk,document,sync_event}_manager`                |
| LLM / embedding adapters    | `core.services.adapters.{llm,embedding}.{registry,base,providers}` |
| Logger                      | `core.services.utils.logger`                                       |
| Chunkers                    | `process_agent.services.chunking_strategies.{heading_aware,recursive}` |
| Ingestion pipelines         | `process_agent.services.ingestion_pipelines.*`                     |
| Prefix generator            | `process_agent.services.llm.prefix_generator`                      |
| Settings / URLs / WSGI      | `core.settings` / `core.urls` / `core.wsgi.application`            |
| Magic values                | `constants` (top-level module)                                     |
