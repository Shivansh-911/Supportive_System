from langchain_core.language_models import BaseChatModel

from constants import ORCHESTRATOR_AGENT_PROVIDER, ORCHESTRATOR_AGENT_MODEL
from core.services.adapters.llm.registry import LLMRegistry
from core.services.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    _model: BaseChatModel | None = None

    @classmethod
    def get_model(cls) -> BaseChatModel:
        if cls._model is None:
            logger.info("[ORCHESTRATOR AGENT initializing LLM model provider=%s model=%s]", ORCHESTRATOR_AGENT_PROVIDER, ORCHESTRATOR_AGENT_MODEL)
            provider = LLMRegistry.get(ORCHESTRATOR_AGENT_PROVIDER)
            cls._model = provider.build(ORCHESTRATOR_AGENT_MODEL)
        return cls._model
