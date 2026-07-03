
from uuid import UUID
import uuid

from pydantic import BaseModel, Field

from question_agent.states.chunk_hit import ChunkHit


class QuestionAgentState(BaseModel):
    request_id: UUID
    question: str
    retrieval_filters: dict = Field(default_factory=dict)

    last_qa_pair: dict | None = None

    query_vector: list[float] | None = None

    vector_hits: list[ChunkHit] = Field(default_factory=list)
    bm25_hits: list[ChunkHit] = Field(default_factory=list)
    fused_candidates: list[ChunkHit] = Field(default_factory=list)

    reranked_chunks: list[ChunkHit] = Field(default_factory=list)

    answer: str | None = None
    cited_chunks: list[ChunkHit] = Field(default_factory=list)
