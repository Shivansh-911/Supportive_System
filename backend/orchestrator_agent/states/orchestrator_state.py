from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class OrchestratorAgentState(BaseModel):
    request_id: UUID
    session_id: int | None = None
    user_id: str
    raw_query: str

    rewritten_query: str | None = None
    intent: Literal["question_agent", "llm"] | None = None
    is_follow_up: bool = False
    session_title: str | None = None

    last_qa_pair: dict | None = None

    response: str | None = None
    metadata: dict = Field(default_factory=dict)
