from django.db import models


class ChunkStrategy(models.TextChoices):
    """Chunking strategy used to produce a chunk."""

    HEADING_AWARE      = 'heading_aware',      'Heading Aware'
    RECURSIVE_FALLBACK = 'recursive_fallback', 'Recursive Fallback'

