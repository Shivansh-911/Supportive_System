from core.services.utils.logger import get_logger
from question_agent.services.embedding_service import EmbeddingService
from question_agent.states.question_agent_state import QuestionAgentState

logger = get_logger(__name__)


def embed_query(state: QuestionAgentState) -> dict:
    logger.info("[REQUEST ID: %s] QUESTION AGENT => embedding question: %s", state.request_id, state.question)
    query_vector = EmbeddingService.get_model().embed_query(state.question)
    logger.info("[REQUEST ID: %s] QUESTION AGENT => embedded query", state.request_id)
    return {"query_vector": query_vector}
