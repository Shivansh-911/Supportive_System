from langchain_openai import OpenAIEmbeddings

from core.services.adapters.embedding.base import BaseEmbeddingProvider


class Provider(BaseEmbeddingProvider):
    def build(self, model_id: str, dimensions: int) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(model=model_id, dimensions=dimensions)
