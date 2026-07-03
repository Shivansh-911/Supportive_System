"""Document model — source of truth for all ingested documents."""

import uuid

from django.db import models
from django.db.models import Q

from constants import CONTENT_HASH_LENGTH
from process_agent.models.sync_event import SyncEvent
from process_agent.managers.document_manager import DocumentManager
from .constants.document_status import DocumentStatus
from core.models.constants.source_type import SourceType


class Document(models.Model):
    """One row per ingested source document.

    Parent record for Chunk — all chunks reference this via doc_id.
    Covers freshdesk_article, freshdesk_ticket, notion_page, and loom_video.
    """

    objects = DocumentManager()

    doc_id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_event_id     = models.ForeignKey(
                            SyncEvent,
                            on_delete=models.SET_NULL,
                            null=True,
                            blank=True,
                            db_column='sync_event_id',
                        )
    source_type       = models.CharField(max_length=50, choices=SourceType.choices)
    source_id         = models.CharField(max_length=255)
    source_title      = models.TextField(blank=True, default='')
    source_url        = models.TextField(blank=True, default='')
    source_created_at = models.DateTimeField(null=True, blank=True)
    source_updated_at = models.DateTimeField(null=True, blank=True)
    source_author     = models.JSONField(default=dict)
    source_metadata   = models.JSONField(default=dict)
    # structured_json   = models.JSONField(null=True, blank=True)
    content_hash      = models.CharField(max_length=CONTENT_HASH_LENGTH)
    cleaned_html      = models.TextField(null=True, blank=True)
    cleaned_text      = models.TextField(blank=True, default='')
    markdown          = models.TextField(blank=True, default='')
    word_count        = models.IntegerField(default=0)
    chunk_count       = models.IntegerField(default=0)
    ingested_at       = models.DateTimeField()
    status            = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.ACTIVE)
    retired_at        = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'document_store'
        constraints = [
            models.UniqueConstraint(
                fields=['source_id', 'source_type'],
                condition=Q(status=DocumentStatus.ACTIVE),
                name='unique_active_document',
            )
        ]
