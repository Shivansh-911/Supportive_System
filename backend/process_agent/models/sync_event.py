"""SyncEvent model — pipeline control table filled by the source worker."""

import uuid

from django.db import models

from process_agent.managers.sync_event_manager import SyncEventManager

from .constants.event_type import EventType
from core.models.constants.source_type import SourceType
from .constants.sync_event_status import SyncEventStatus


class SyncEvent(models.Model):
    """Tracks every source event from intake through ingestion completion.

    Filled by the source worker; consumed by the outbox worker. Never deleted —
    permanent audit trail.
    """

    objects = SyncEventManager()

    event_id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_id               = models.CharField(max_length=255)
    source_type             = models.CharField(max_length=50, choices=SourceType.choices)
    source_title            = models.TextField(blank=True, default='')
    source_url              = models.TextField(blank=True, default='')
    event_type              = models.CharField(max_length=20, choices=EventType.choices)
    source_updated_at       = models.DateTimeField(null=True, blank=True)
    detected_at             = models.DateTimeField(auto_now_add=True)
    source_payload          = models.JSONField(default=dict)
    status                  = models.CharField(max_length=20, choices=SyncEventStatus.choices, default=SyncEventStatus.PENDING)
    actioned_by             = models.CharField(max_length=255, null=True, blank=True)
    actioned_at             = models.DateTimeField(null=True, blank=True)
    processing_started_at   = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    retry_count             = models.IntegerField(default=0)
    next_retry_at           = models.DateTimeField(null=True, blank=True)
    error_stage             = models.CharField(max_length=100, null=True, blank=True)
    error_message           = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'sync_events'
        constraints = [
            models.UniqueConstraint(
                fields=['source_id', 'source_type', 'detected_at'],
                name='unique_sync_event',
            )
        ]

