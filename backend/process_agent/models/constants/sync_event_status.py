from django.db import models


class SyncEventStatus(models.TextChoices):
    """Lifecycle status of a sync event."""

    PENDING    = 'pending',    'Pending'
    APPROVED   = 'approved',   'Approved'
    REJECTED   = 'rejected',   'Rejected'
    PROCESSING = 'processing', 'Processing'
    COMPLETED  = 'completed',  'Completed'
    FAILED     = 'failed',     'Failed'
