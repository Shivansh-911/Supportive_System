# Architecture Decisions

---

## 1. Pipeline Transaction Strategy

### Decision
Use two small `transaction.atomic()` blocks around DB operations only. Do not wrap the entire pipeline in a single transaction.

### Context
The ingestion pipeline involves external API calls (Voyage embedding, Haiku for context_prefix generation). A failed pipeline step (e.g. embedding) can leave partial state in the DB — a `document_store` row with no chunks, or chunks with no embeddings.

A full pipeline transaction was considered to solve this but rejected.

### Why not a full transaction
- DB connections are held open for the entire duration of external API calls (seconds to minutes under load)
- Connection pool exhaustion under concurrent ingestion
- Postgres locks are held while waiting on Anthropic/Voyage APIs
- No practical benefit — if the process crashes, Postgres rolls back automatically anyway

### Chosen approach

```
Transaction 1  (DB only — fast)
  → delete existing document_store row + chunks (CASCADE)
  → insert fresh document_store row with status = processing

  [ API calls — outside any transaction ]
  → cleaning service
  → chunking service
  → embedding API (Voyage)
  → context_prefix generation (Haiku)

Transaction 2  (DB only — fast)
  → bulk insert all chunks
  → update document_store status → active
  → update sync_event status → completed
```

If anything in the API call section fails:
- Transaction 2 never runs
- `document_store` row remains with `status = processing`
- `error_stage` and `error_message` are written via a separate small update
- Outbox worker schedules retry via `next_retry_at`
- On retry: Transaction 1 cleans up partial state and starts fresh

### Content hash on retry
The content_hash check (used to skip unchanged documents) must be status-aware:

| Existing document state | Hash matches | Action |
|---|---|---|
| `status = active` | yes | skip — document unchanged |
| `status = active` | no  | re-ingest — document updated at source |
| document exists, previous run failed | any | ignore hash — delete and re-run |

### Rule
`transaction.atomic()` wraps DB writes only — never external I/O.

---
