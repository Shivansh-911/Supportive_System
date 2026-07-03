from django.db import models
from django.utils import timezone


class SyncEventManager(models.Manager):

    def mark_processing(self, event) -> None:
        event.status = 'processing'
        event.processing_started_at = timezone.now()
        event.save(update_fields=['status', 'processing_started_at'])

    def mark_skipped(self, event, reason: str) -> None:
        event.error_message = reason
        event.save(update_fields=['error_message'])
