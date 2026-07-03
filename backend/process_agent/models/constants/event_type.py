from django.db import models


class EventType(models.TextChoices):
    """Type of change detected at the source."""

    CREATED = 'created', 'Created'
    UPDATED = 'updated', 'Updated'
    DELETED = 'deleted', 'Deleted'
