import importlib

from core.services.adapters.llm.base import BaseLLMProvider


class LLMRegistry:
    # Lazy-loads provider modules by path so unused SDKs are never imported at startup.
    _registry: dict[str, str] = {
        "anthropic": "core.services.adapters.llm.providers.anthropic",
        "openai":    "core.services.adapters.llm.providers.openai",
    }

    @classmethod
    def get(cls, provider: str) -> BaseLLMProvider:
        if provider not in cls._registry:
            raise ValueError(f"Unknown provider: {provider!r}")
        module = importlib.import_module(cls._registry[provider])
        return module.Provider()
