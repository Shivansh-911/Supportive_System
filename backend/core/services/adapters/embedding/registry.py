import importlib

from core.services.adapters.embedding.base import BaseEmbeddingProvider


class EmbeddingRegistry:
    _registry: dict[str, str] = {
        "openai": "core.services.adapters.embedding.providers.openai",
    }

    @classmethod
    def get(cls, provider: str) -> BaseEmbeddingProvider:
        if provider not in cls._registry:
            raise ValueError(f"Unknown embedding provider: {provider!r}")
        module = importlib.import_module(cls._registry[provider])
        return module.Provider()
