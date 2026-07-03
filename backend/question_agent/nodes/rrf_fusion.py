from constants import RRF_BM25_WEIGHT, RRF_K, RRF_VECTOR_WEIGHT, TOP_K_FUSED
from core.services.utils.logger import get_logger
from question_agent.services.rrf_service import RRFService
from question_agent.states.question_agent_state import QuestionAgentState

logger = get_logger(__name__)


def rrf_fusion(state: QuestionAgentState) -> dict:

    fused = RRFService().fuse_rankings(
        ranked_lists=[state.vector_hits, state.bm25_hits],
        k=RRF_K,
        top_n=TOP_K_FUSED,
        weights=[RRF_VECTOR_WEIGHT, RRF_BM25_WEIGHT],
    )

    logger.info("[REQUEST ID: %s] QUESTION AGENT => rrf fusion produced %d candidates",state.request_id,len(fused))
    
    return {"fused_candidates": fused}
