from django.db import models


class DocumentStatus(models.TextChoices):
    """Lifecycle status of an ingested document."""

    ACTIVE  = 'active',  'Active'
    RETIRED = 'retired', 'Retired'
