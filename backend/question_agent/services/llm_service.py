from langchain_core.language_models import BaseChatModel

from constants import QUESTION_AGENT_PROVIDER, QUESTION_AGENT_ANSWER_MODEL
from core.services.adapters.llm.registry import LLMRegistry


class LLMService:
    _model: BaseChatModel | None = None

    @classmethod
    def get_model(cls) -> BaseChatModel:
        if cls._model is None:
            provider = LLMRegistry.get(QUESTION_AGENT_PROVIDER)
            cls._model = provider.build(QUESTION_AGENT_ANSWER_MODEL)
        return cls._model
