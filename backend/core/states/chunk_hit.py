from uuid import UUID

from pydantic import BaseModel


class ChunkHit(BaseModel):
    chunk_id: UUID
    doc_id: UUID
    score: float
    content: str
    

    model_config = {'frozen': True}
