"""Chunk model — embedding units produced by the pipeline chunker."""

import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from pgvector.django import HnswIndex, VectorField

from constants import EMBEDDING_DIMENSIONS, HNSW_EF_CONSTRUCTION, HNSW_M
from core.managers.chunk_manager import ChunkManager
from process_agent.models.document import Document
from .constants.chunk_strategy import ChunkStrategy
from .constants.source_type import SourceType


class Chunk(models.Model):
    """One row per chunk per document. Deleted and replaced on every re-ingest.

    Denormalizes source_type, source_id, and source_url from Document to avoid
    joins at retrieval time.
    """

    objects = ChunkManager()

    chunk_id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doc_id          = models.ForeignKey(Document, on_delete=models.CASCADE, db_column='doc_id')
    source_type     = models.CharField(max_length=50, choices=SourceType.choices)
    source_id       = models.CharField(max_length=255)
    source_url      = models.TextField(blank=True, default='')
    position        = models.IntegerField()
    content         = models.TextField()
    searchable_text = models.TextField()
    embedding       = VectorField(dimensions=EMBEDDING_DIMENSIONS)
    model_id        = models.CharField(max_length=255)
    content_tsv     = models.GeneratedField(
        expression=SearchVector('searchable_text', config='english'),
        output_field=SearchVectorField(),
        db_persist=True,
    )
    token_count     = models.IntegerField(default=0)
    chunk_strategy  = models.CharField(max_length=50, choices=ChunkStrategy.choices)
    context_prefix  = models.TextField(null=True, blank=True)
    chunk_metadata        = models.JSONField(default=dict)
    created_at      = models.DateTimeField(auto_now_add=True)
    deleted         = models.BooleanField(default=None)
    deleted_at      = models.DateTimeField()

    class Meta:
        db_table = 'chunks'
        indexes = [
            HnswIndex(
                fields=['embedding'],
                m=HNSW_M,
                ef_construction=HNSW_EF_CONSTRUCTION,
                opclasses=['vector_cosine_ops'],
                name='chunks_embedding_hnsw',
            ),
            GinIndex(fields=['content_tsv'], name='chunks_content_tsv_gin'),
            # models.Index(fields=['source_type'], name='chunks_source_type_btree'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['doc_id', 'position'],
                name='unique_chunk_position',
            )
        ]

