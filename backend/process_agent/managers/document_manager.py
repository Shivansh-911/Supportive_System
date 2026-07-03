import uuid
from django.db import models
from django.utils import timezone

from process_agent.models.constants.document_status import DocumentStatus


class DocumentManager(models.Manager):

    def get_existing_hash(self, source_id: str, source_type: str) -> str | None:
        doc = self.filter(source_id=source_id, source_type=source_type, status=DocumentStatus.ACTIVE).first()
        return doc.content_hash if doc else None

    def get_active_document(self, source_id: str, source_type: str):
        return self.filter(source_id=source_id, source_type=source_type, status=DocumentStatus.ACTIVE).first()


    def retire_document(self, doc):
        doc.status      = DocumentStatus.RETIRED
        doc.retired_at  = timezone.now()
        doc.chunk_count = 0
        doc.save(update_fields=['status', 'retired_at', 'chunk_count'])

    def insert_document(
        self,
        event_id: uuid.UUID,
        source_id: str,
        source_type: str,
        source_title: str,
        source_url: str,
        source_created_at,
        source_updated_at,
        content_hash: str,
        cleaned_html: str,
        cleaned_text: str,
        markdown: str,
        source_author: dict | None = None,
        source_metadata: dict | None = None,
    ):
        return self.create(
            sync_event_id=event_id,
            source_type=source_type,
            source_id=source_id,
            source_title=source_title,
            source_url=source_url,
            source_created_at=source_created_at,
            source_updated_at=source_updated_at,
            source_author=source_author or {},
            source_metadata=source_metadata or {},
            content_hash=content_hash,
            cleaned_html=cleaned_html,
            cleaned_text=cleaned_text,
            markdown=markdown,
            chunk_count=0,
            word_count=len(cleaned_text.split()),
            ingested_at=timezone.now(),
            status=DocumentStatus.ACTIVE,
            retired_at=None,
        )
