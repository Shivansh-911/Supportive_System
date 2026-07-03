# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt
# Run the development server
python manage.py runserver
# Apply migrations
python manage.py migrate
# Run the outbox worker (polls sync_events, dispatches to process agent)
python manage.py run_outbox_worker
# Run the process agent directly against a single event
python manage.py run_process_agent
# Django shell
python manage.py shell
```

There is no test suite yet. Settings live in a single `core/settings.py` module. The active environment is selected at startup by `DJANGO_ENV` (one of `development`, `beta`, `production` — defaults to `development`), which loads the matching `.env.{DJANGO_ENV}` file at the project root via `django-environ`. All env-specific values (DEBUG, ALLOWED_HOSTS, HSTS/SSL flags, DATABASE_URL, SECRET_KEY) come from that env file.

---

## Architecture

### 3-Layer Rule

```
Layer 1 — Presentation   →   views.py · serializers.py · urls.py
Layer 2 — Business Logic →   services/
Layer 3 — Data Access    →   models/ · managers/ · migrations/
```

**Views call Services. Services call Managers. Nothing skips a layer.**

### Django Apps

| App | Responsibility |
|---|---|
| `pipeline/` | Core ingestion models, managers, ABCs, registries, and Freshdesk implementations |
| `agents/` | LangGraph `process_agent` — orchestrates the full ingestion pipeline |
| `outbox/` | Outbox worker that polls `sync_events` and dispatches to `process_agent` |

### Shared Infrastructure (not Django apps)

| Path | Responsibility |
|---|---|
| `adapters/llm/` | Provider-agnostic LLM adapter; factory selects from `constants.py` |
| `adapters/embedding/` | Provider-agnostic embedding adapter (default: Voyage) |
| `chunking_strategies/` | `heading_aware` and `recursive_fallback` chunkers |
| `llm/prefix_generator.py` | Generates context prefix for each chunk (runs between chunk and embed steps) |
| `constants.py` | **All magic values** — model names, dimensions, thresholds. Always add new constants here. |
| `exceptions.py` | `IngestionError`, `EmbeddingError`, etc. |

---

Implementation refer the below docs:-
  Process Agent : `docs/PROCESS_AGENT.md`
  File Structure : `docs/FILE_STRUCTURE.md`
  DataBase : `docs/DATABASE.md`
  Coding standards : `docs/CONVENTIONS.md`

