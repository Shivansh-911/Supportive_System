from constants import TOP_K_CHUNKS_VECTOR
from core.models.chunk import Chunk
from core.services.utils.logger import get_logger
from question_agent.states.chunk_hit import ChunkHit
from question_agent.states.question_agent_state import QuestionAgentState

logger = get_logger(__name__)


def vector_search(state: QuestionAgentState) -> dict:
    
    rows = Chunk.objects.vector_search(
        query_vector=state.query_vector,
        top_k=TOP_K_CHUNKS_VECTOR,
        filters=state.retrieval_filters or None,
    )
    hits = []
    for row in rows:
        hits.append(
            ChunkHit(
                chunk_id=row["chunk_id"],
                doc_id=row["doc_id"],
                content=row["content"],
                score=row["score"],
            )
        )
    logger.info("[REQUEST ID: %s] QUESTION AGENT => vector search returned %d hits",state.request_id,len(hits))
    return {"vector_hits": hits}
