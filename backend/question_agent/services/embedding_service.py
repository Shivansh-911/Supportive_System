from langchain_core.embeddings import Embeddings

from constants import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, EMBEDDING_PROVIDER
from core.services.adapters.embedding.registry import EmbeddingRegistry


class EmbeddingService:
    _model: Embeddings | None = None

    @classmethod
    def get_model(cls) -> Embeddings:
        if cls._model is None:
            provider = EmbeddingRegistry.get(EMBEDDING_PROVIDER)
            cls._model = provider.build(EMBEDDING_MODEL, EMBEDDING_DIMENSIONS)
        return cls._model
