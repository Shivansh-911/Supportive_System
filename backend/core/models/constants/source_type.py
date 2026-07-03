from django.db import models


class SourceType(models.TextChoices):
    """Supported ingestion source types."""

    FRESHDESK_ARTICLE = 'freshdesk', 'Freshdesk'
    FRESHDESK_TICKET  = 'freshdesk_ticket',  'Freshdesk Ticket'
    NOTION_PAGE       = 'notion_page',       'Notion Page'
    LOOM_VIDEO        = 'loom_video',        'Loom Video'
