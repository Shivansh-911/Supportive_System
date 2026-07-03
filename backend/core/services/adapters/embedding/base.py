from abc import ABC, abstractmethod

from langchain_core.embeddings import Embeddings


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def build(self, model_id: str, dimensions: int) -> Embeddings: ...
