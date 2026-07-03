from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel


class BaseLLMProvider(ABC):
    @abstractmethod
    def build(self, model_id: str) -> BaseChatModel: ...
