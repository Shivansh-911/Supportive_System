from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db import models
from django.db.models import F
from pgvector.django import CosineDistance


class ChunkManager(models.Manager):

    def delete_chunks_for_document(self, doc_id) -> int:
        deleted, _ = self.filter(doc_id=doc_id).delete()
        return deleted

    def vector_search(self, query_vector: list[float], top_k: int, filters: dict | None = None) -> list[dict]:
        query_set = self.all()
        if filters:
            query_set = query_set.filter(**filters)
        return list(
            query_set.annotate(distance=CosineDistance('embedding', query_vector))
                     .annotate(score=1 - F('distance'))
                     .order_by('distance')
                     .values('chunk_id', 'doc_id', 'content', 'score')[:top_k]
        )

    def bm25_search(self, question: str, top_k: int, filters: dict | None = None) -> list[dict]:
        search_query = SearchQuery(question, search_type='plain', config='english')                             # plainto => join all words with AND , websearch => has logical support
        query_set = self.filter(content_tsv=search_query)
        if filters:
            query_set = query_set.filter(**filters)
        return list(
            query_set.annotate(score=SearchRank(F('content_tsv'), search_query, cover_density=True))                # cd => takes relative distance in account between words
                     .order_by('-score')
                     .values('chunk_id', 'doc_id', 'content', 'score')[:top_k]
        )

    def bulk_insert_chunks(
        self,
        doc,
        source_type: str,
        source_id: str,
        source_url: str,
        model_id: str,
        rows: list[dict],
    ) -> list:
        chunks = [
            self.model(
                doc_id=doc,
                source_type=source_type,
                source_id=source_id,
                source_url=source_url,
                position=position,
                content=row['content'],
                searchable_text=row['searchable_text'],
                embedding=row['embedding'],
                model_id=model_id,
                token_count=row['token_count'],
                chunk_strategy=row['chunk_strategy'],
                context_prefix=row['context_prefix'],
                chunk_metadata=row['chunk_metadata'],
            )
            for position, row in enumerate(rows)
        ]
        return self.bulk_create(chunks)

    def get_source_url_and_image_map(self, chunk_id) -> dict:
        row = self.filter(chunk_id=chunk_id).values('source_url', 'chunk_metadata').get()
        return {
            'source_url': row['source_url'],
            'image_map':  row['chunk_metadata'].get('image_map', {}),
        }
