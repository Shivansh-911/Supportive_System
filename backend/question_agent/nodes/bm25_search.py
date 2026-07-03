from constants import TOP_K_CHUNKS_BM25
from core.models.chunk import Chunk
from core.services.utils.logger import get_logger
from question_agent.states.chunk_hit import ChunkHit
from question_agent.states.question_agent_state import QuestionAgentState

logger = get_logger(__name__)


def bm25_search(state: QuestionAgentState) -> dict:
    
    rows = Chunk.objects.bm25_search(
        question=state.question,
        top_k=TOP_K_CHUNKS_BM25,
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
    logger.info("[REQUEST ID: %s] QUESTION AGENT => bm25 search returned %d hits",state.request_id,len(hits))
    return {"bm25_hits": hits}
