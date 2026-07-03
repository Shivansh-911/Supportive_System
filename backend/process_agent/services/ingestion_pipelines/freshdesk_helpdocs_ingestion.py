import logging

from django.db import transaction
from langchain_core.embeddings import Embeddings

from constants import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    PROCESS_AGENT_CONTEXT_MODEL,
    PROCESS_AGENT_PROVIDER,
)
from core.services.adapters.llm.registry import LLMRegistry
from core.services.adapters.embedding.registry import EmbeddingRegistry
from process_agent.services.llm.prefix_generator import PrefixGenerator
from core.models.chunk import Chunk
from process_agent.models.document import Document
from process_agent.models.sync_event import SyncEvent
from process_agent.services.ingestion_pipelines.base_ingestion import BaseIngestion
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs.freshdesk_cleaner import FreshdeskCleaner
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs.freshdesk_structurer import FreshdeskStructurer
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs.freshdesk_helper import FreshdeskHelper
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs.freshdesk_chunk_helper import FreshdeskChunkHelper
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs.freshdesk_context_retrieval import FreshdeskContextRetrieval
from process_agent.services.ingestion_pipelines.freshdesk_helpdocs.freshdesk_convet_to_markdown import FreshdeskConvertToMarkdown
from process_agent.services.chunking_strategies.heading_aware import HeadingAwareChunker
from process_agent.services.chunking_strategies.recursive import RecursiveChunker

logger = logging.getLogger(__name__)


class FreshdeskHelpdocsIngestion(BaseIngestion):

    def __init__(
        self,
        helper: FreshdeskHelper,
        cleaner: FreshdeskCleaner,
        structurer: FreshdeskStructurer,
        convert_to_markdown: FreshdeskConvertToMarkdown,
        heading_chunker: HeadingAwareChunker,
        recursive_chunker: RecursiveChunker,
        chunk_helper: FreshdeskChunkHelper,
        context_retrieval: FreshdeskContextRetrieval,
        prefix_generator: PrefixGenerator,
        embedding_model: Embeddings,
    ) -> None:
        self._helper = helper
        self._cleaner = cleaner
        self._structurer = structurer
        self._convert_to_markdown = convert_to_markdown
        self._heading_chunker = heading_chunker
        self._recursive_chunker = recursive_chunker
        self._chunk_helper = chunk_helper
        self._context_retrieval = context_retrieval
        self._prefix_generator = prefix_generator
        self._embedding_model = embedding_model

    @classmethod
    def create(cls) -> "FreshdeskHelpdocsIngestion":
        llm_provider = LLMRegistry.get(PROCESS_AGENT_PROVIDER)
        llm = llm_provider.build(PROCESS_AGENT_CONTEXT_MODEL)

        embedding_provider = EmbeddingRegistry.get(EMBEDDING_PROVIDER)
        embedding_model = embedding_provider.build(EMBEDDING_MODEL, EMBEDDING_DIMENSIONS)

        return cls(
            helper=FreshdeskHelper(),
            cleaner=FreshdeskCleaner(),
            structurer=FreshdeskStructurer(),
            convert_to_markdown=FreshdeskConvertToMarkdown(),
            heading_chunker=HeadingAwareChunker(),
            recursive_chunker=RecursiveChunker(),
            chunk_helper=FreshdeskChunkHelper(),
            context_retrieval=FreshdeskContextRetrieval(llm),
            prefix_generator=PrefixGenerator(llm),
            embedding_model=embedding_model,
        )

    # ── Orchestrator ──────────────────────────────────────────────────────────

    def ingest(self, event: SyncEvent) -> None:
        logger.info("Starting Freshdesk helpdocs ingestion for event_id=%s", event.event_id)

        # Step 1: Destructure event
        source_id         = event.source_id
        source_type       = event.source_type
        source_title      = event.source_title
        source_url        = event.source_url
        source_created_at = event.source_created_at
        source_updated_at = event.source_updated_at
        raw_payload       = event.source_payload
        logger.debug(
            "Step 1: Destructured event source_id=%s source_type=%s source_title=%r",
            source_id, source_type, source_title,
        )

        # Step 2: Content hash — generate, compare, decide skip or proceed
        content_hash  = self._helper.generate_hash(raw_payload)
        existing_hash = Document.objects.get_existing_hash(source_id, source_type)
        if content_hash == existing_hash:
            logger.info(
                "Step 2: Content hash unchanged for source_id=%s; skipping ingestion",
                source_id,
            )
            return
        logger.debug(
            "Step 2: Content hash changed for source_id=%s (new=%s, existing=%s); proceeding",
            source_id, content_hash, existing_hash,
        )

        # Step 3: Clean raw HTML
        cleaned_html, cleaned_text = self._cleaner.clean(raw_payload.get('description', ''))
        logger.debug(
            "Step 3: Cleaned HTML for source_id=%s (html_len=%d, text_len=%d)",
            source_id, len(cleaned_html), len(cleaned_text),
        )

        # Step 4: Convert cleaned HTML into markdown
        markdown, has_heading = self._convert_to_markdown.toMarkdown(cleaned_html)
        logger.debug(
            "Step 4: Converted to markdown for source_id=%s (markdown_len=%d, has_heading=%s)",
            source_id, len(markdown), has_heading,
        )

        # Step 5: Build author + metadata bins from payload
        source_author, source_metadata = self._helper.metadata_creator(raw_payload)
        logger.debug(
            "Step 5: Built metadata for source_id=%s (author=%r, metadata_keys=%s)",
            source_id, source_author, list(source_metadata.keys()),
        )

        # Step 6: Replace image URLs with <img N> placeholders + build the document-level image map
        no_img_url_markdown, document_image_map = self._helper.replace_image_links(markdown)
        logger.debug(
            "Step 6: Replaced image links for source_id=%s (image_count=%d)",
            source_id, len(document_image_map),
        )

        # Step 7: Chunk the markdown. Heading-aware where a heading structure exists,
        # recursive fallback otherwise.
        if has_heading:
            chunks = self._heading_chunker.heading_aware(no_img_url_markdown)
            logger.debug(
                "Step 7: Heading-aware chunking produced %d chunks for source_id=%s",
                len(chunks), source_id,
            )
        else:
            chunks = self._recursive_chunker.recursive(no_img_url_markdown)
            logger.debug(
                "Step 7: Recursive chunking produced %d chunks for source_id=%s",
                len(chunks), source_id,
            )

        # Step 8: For each chunk — swap image links for [Img N], generate context prefix,
        #         build chunk metadata, and assemble the searchable text.
        category_name = source_metadata.get('category_name')
        folder_name   = source_metadata.get('folder_name')

        chunk_rows: list[dict] = []
        for index, (chunk_text, _, chunk_strategy) in enumerate(chunks):
            logger.debug(
                "Step 8: Processing chunk %d/%d for source_id=%s (strategy=%s)",
                index + 1, len(chunks), source_id, chunk_strategy,
            )
            chunk_image_map = self._chunk_helper.build_chunk_image_map(chunk_text, document_image_map)
            # context_prefix  = self._context_retrieval.retrieve(source_title, markdown, chunk_text)
            context_prefix = ""
            chunk_metadata  = self._chunk_helper.build_chunk_metadata(source_metadata, source_author, chunk_image_map)
            searchable_text, token_count = self._chunk_helper.build_searchable_chunk(
                category_name,
                folder_name,
                source_title,
                context_prefix,
                chunk_text,
            )
            chunk_rows.append({
                'content':         chunk_text,
                'searchable_text': searchable_text,
                'token_count':     token_count,
                'context_prefix':  context_prefix,
                'chunk_metadata':  chunk_metadata,
                'chunk_strategy':  chunk_strategy,
            })
        logger.info(
            "Step 8: Built %d chunk rows for source_id=%s",
            len(chunk_rows), source_id,
        )

        # Step 9: Batch-embed the searchable text and attach each vector to its row.
        logger.info(
            "Step 9: Embedding %d chunks for source_id=%s using model=%s",
            len(chunk_rows), source_id, EMBEDDING_MODEL,
        )
        embeddings = self._embedding_model.embed_documents(
            [row['searchable_text'] for row in chunk_rows]
        )
        for row, vector in zip(chunk_rows, embeddings):
            row['embedding'] = vector
        logger.debug(
            "Step 9: Attached %d embedding vectors for source_id=%s",
            len(embeddings), source_id,
        )

        # Step 10: Single short atomic write — retire old doc + its chunks, insert new doc + chunks.
        # All slow work (LLM, embedding) is already done; this block contains only Postgres writes.
        with transaction.atomic():
            old_doc = Document.objects.get_active_document(source_id, source_type)
            if old_doc:
                logger.info(
                    "Step 10: Retiring existing document doc_id=%s for source_id=%s",
                    old_doc.doc_id, source_id,
                )
                Chunk.objects.delete_chunks_for_document(old_doc.doc_id)
                Document.objects.retire_document(old_doc)

            new_doc = Document.objects.insert_document(
                event,
                source_id,
                source_type,
                source_title,
                source_url,
                source_created_at,
                source_updated_at,
                content_hash,
                cleaned_html,
                cleaned_text,
                markdown,
                source_author,
                source_metadata,
            )
            logger.info(
                "Step 10: Inserted new document doc_id=%s for source_id=%s",
                new_doc.doc_id, source_id,
            )

            Chunk.objects.bulk_insert_chunks(
                doc=new_doc,
                source_type=source_type,
                source_id=source_id,
                source_url=source_url,
                model_id=EMBEDDING_MODEL,
                rows=chunk_rows,
            )
            logger.info(
                "Step 10: Persisted %d chunks for doc_id=%s source_id=%s",
                len(chunk_rows), new_doc.doc_id, source_id,
            )

        logger.info(
            "Completed Freshdesk helpdocs ingestion for event_id=%s source_id=%s",
            event.event_id, source_id,
        )
