# Future Flags

Deferred items to revisit. Not blocking current work.

---

## Freshdesk `generate_hash` is too narrow

**Where:** `Process_Agent/services/freshdesk_helpdocs/freshdesk_helper.py` → `FreshdeskHelper.generate_hash`

**Current behavior:** Hashes only `desc_un_html` (cleaned body text).

**Problem:** The following payload changes will *silently* not trigger re-ingest, even though they affect what we embed or filter on at retrieval:

- `title` edited — title typically appears in `context_prefix` / searchable text
- Article moved between folders/categories (`folder_id`, `folder_name`, `category_id`, `category_name`)
- `tags` added/removed
- `status` flipped (1 = draft → 2 = published, or vice versa) — at minimum a draft transition should retire the active row

**Suggested fix when revisited:**

```python
def generate_hash(self, payload: dict) -> str:
    material = {
        "desc":        payload.get("desc_un_html", ""),
        "title":       payload.get("title", ""),
        "tags":        sorted(payload.get("tags", [])),
        "folder_id":   payload.get("folder_id"),
        "category_id": payload.get("category_id"),
        "status":      payload.get("status"),
    }
    return hashlib.sha256(
        json.dumps(material, sort_keys=True).encode()
    ).hexdigest()
```

**Do NOT include** in hash material: `hits`, `thumbs_up`, `thumbs_down`, `updated_at`, `modified_at` — these churn on read traffic and would force unnecessary re-embeds.

**Trigger to act:** First time we see a retrieval bug caused by stale title/taxonomy, or before going to prod — whichever comes first.

---

## Per-section recursive split for oversized heading sections

**Where:** `chunking_strategies/heading_aware.py` → `HeadingAwareChunker.heading_aware` (between section extraction at line ~46 and the `_merge_small_sections` call at line ~52)

**Current behavior:** Sections from `MarkdownHeaderTextSplitter` go directly into `_merge_small_sections`, which only grows small sections — never splits large ones. `CHUNK_SINGLE_MAX_TOKENS` acts as a trigger for "needs splitting", not as an upper bound after the heading split.

**Problem:** A single H2/H3 section that is already over MAX passes through unchanged. The headingless fallback (`self._fallback.recursive(...)` at line 49) does not fire because `len(sections) > 1`. Audit examples:

- Article 89000018737 → 952-token chunk (one oversized section under "Slot Types")
- Article 89000017927 → 868-token first chunk (intro + notes + steps + screenshots all under the first H2 before the next H2 fires)
- Articles 89000019916 (733), 89000018610 (676), 89000018124 (668)

Result: ~5% of chunks are 2–3× the size cap. Embedding vectors become diffuse; narrow queries retrieve mixed-topic chunks.

**Suggested fix when revisited:**

```python
def _expand_oversized(self, sections: list[str]) -> list[str]:
    expanded: list[str] = []
    for section in sections:
        if self._count_tokens(section) <= CHUNK_SINGLE_MAX_TOKENS:
            expanded.append(section)
            continue
        heading_line = section.splitlines()[0] if section.startswith("#") else ""
        for sub_text, _ in self._fallback.recursive(section):
            if heading_line and not sub_text.startswith(heading_line):
                sub_text = f"{heading_line}\n\n{sub_text}"
            expanded.append(sub_text)
    return expanded
```

Wire as `sections = self._expand_oversized(sections)` between the section build and `self._merge_small_sections(sections)`.

**Do NOT enable without** heading-prefix prepending on sub-pieces. Splitting without it breaks "click X then click Y" continuity in help docs — sub-piece 2 loses its parent context and reads as a standalone fragment.

**Tradeoff being accepted by deferring:** ~5% of chunks remain oversized. Embedding precision on those chunks is lower than it could be. Partially compensated by the 50-token overlap in `RecursiveChunker` and by top-k retrieval reconstructing adjacency at synthesis time. The deferred fix would tighten precision at the cost of authored-section continuity.

**Trigger to act:** First retrieval evaluation showing oversized chunks dominating top-k for narrow queries. Or: first audit re-run that still shows >5% of chunks above 600 tokens after the headingless fallback ships.

---

## Prompt caching for `FreshdeskContextRetrieval`

**Where:** `Process_Agent/services/freshdesk_helpdocs/freshdesk_context_retrieval.py` → `FreshdeskContextRetrieval.retrieve`, called per-chunk from `Process_Agent/services/freshdesk_helpdocs_ingestion.py`.

**Current behavior:** For every chunk in an article we make a fresh LLM call sending `system_prompt + article_title + full_markdown + chunk`. The system prompt and the document are identical across all chunks of a single article — only the chunk text rotates — so we re-bill the static prefix N times per article.

**Problem:** Token cost scales linearly with chunks-per-article. For a 2000-token doc split into 10 chunks we bill ~20,000 input tokens for content the provider has already seen 9 times in the same ingestion run.

**Suggested fix when revisited:** Use Anthropic ephemeral prompt caching (provider is already `anthropic` per `constants.PROCESS_AGENT_PROVIDER`). Restructure the `HumanMessage` into content blocks and mark the doc block with `cache_control={"type": "ephemeral"}`; keep the chunk block uncached so each call rotates only the chunk text. The `SystemMessage` should also be cached.

Approximate billing model (2000-token doc, 10 chunks):

| Strategy | Input units |
|---|---|
| No cache (today) | 20,000 |
| Anthropic ephemeral (1.25× write, 0.1× read) | ~4,300 |
| OpenAI auto-cache (0.5× read, no write surcharge) | ~11,000 |

**Do NOT enable without** verifying the 5-minute TTL fits the ingestion-run latency for a single article. If chunks of one article ever get processed >5 min apart (e.g. async fan-out) the cache will miss and we pay the 1.25× write penalty repeatedly — worse than no caching.

**Tradeoff being accepted by deferring:** Every ingestion run pays full input cost for the doc N times per article. Fine while volume is low; will matter once we batch-ingest historical content or onboard a larger Freshdesk corpus.

**Trigger to act:** First time monthly LLM spend on context generation crosses a threshold worth optimizing, OR before any bulk back-fill of existing articles.

---

## Strip raw image URLs from doc passed to context retrieval

**Where:** `Process_Agent/services/freshdesk_helpdocs_ingestion.py` — call site of `self._context_retrieval.retrieve(source_title, markdown, replaced_text)`.

**Current behavior:** The chunk passed to context retrieval has freshdesk image URLs rewritten to `[Img N]` placeholders by `FreshdeskChunkHelper`, but the full `markdown` doc is sent as-is — still containing the long raw S3 URLs. The system prompt explicitly tells the LLM that the placeholders and the raw URLs refer to the same images, so it doesn't get confused, but the URLs still consume input tokens.

**Problem:** S3 image URLs are ~150 chars each. A doc with 6 images burns ~900+ characters of tokens that contribute nothing to context generation — the LLM only needs to know an image exists at that position, not where it lives. Combined with N-chunks-per-article fan-out, this multiplies.

**Suggested fix when revisited:** Run `markdown` through `FreshdeskChunkHelper.replace_image_links` once before the per-chunk loop, pass the rewritten doc + rewritten chunk to `retrieve`, and simplify the system prompt back to "all image URLs are replaced with `[Img N]`" (drop the "raw URLs in the doc" caveat). Image numbering between doc and chunk will differ (doc is numbered across the whole article; chunk is numbered locally), so either re-state that in the prompt or accept the asymmetry — the LLM only needs the *concept* that placeholders mean images, not a matching index.

**Do NOT enable without** deciding the indexing convention. If the doc says `[Img 7]` but the chunk says `[Img 1]` for the same image, the LLM may try to correlate by number and hallucinate. Safest: use a non-numeric placeholder like `[image]` in the doc, keep `[Img N]` in the chunk.

**Tradeoff being accepted by deferring:** Every context-generation call carries dead URL tokens. Cost is small per call but compounds with chunk count and back-fill volume. Stacks with the prompt-caching flag above — if caching lands first, this becomes lower priority since the doc is paid once per article anyway.

**Trigger to act:** Together with the prompt-caching work, or sooner if a single-article ingestion shows the doc-token share dominating context-generation cost.
