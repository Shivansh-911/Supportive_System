from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from core.services.utils.logger import get_logger
from orchestrator_agent.services.llm_service import LLMService
from orchestrator_agent.services.prompts.classify_intent_prompt import SYSTEM, USER_TEMPLATE
from orchestrator_agent.states.orchestrator_state import OrchestratorAgentState

logger = get_logger(__name__)


class ClassifyAndRewriteOutput(BaseModel):
    intent: Literal["question_agent", "llm"]
    is_follow_up: bool
    rewritten_query: str
    title: str | None = None


def classify_and_rewrite(state: OrchestratorAgentState) -> dict:
    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => classifying intent and rewriting query", state.request_id)
    last_question = ""
    last_answer = ""
    last_intent = ""
    if state.last_qa_pair:
        last_question = state.last_qa_pair.get("question", "")
        last_answer = state.last_qa_pair.get("answer", "")
        last_intent = state.last_qa_pair.get("intent", "")

    needs_title = state.session_title is None
    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => [needs title = %s]", state.request_id, needs_title)
    user_message = USER_TEMPLATE.format(
        query=state.raw_query,
        last_question=last_question or "None",
        last_answer=last_answer or "None",
        last_intent=last_intent or "None",
        needs_title=needs_title,
    )

    model = LLMService.get_model().with_structured_output(ClassifyAndRewriteOutput)
    result: ClassifyAndRewriteOutput = model.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=user_message),
    ])

    logger.info(
        "[REQUEST ID: %s] ORCHESTRATOR AGENT => classified [intent = %s] [is_follow_up = %s]",state.request_id,result.intent,result.is_follow_up)
    return {
        "intent": result.intent,
        "is_follow_up": result.is_follow_up,
        "rewritten_query": result.rewritten_query,
        "session_title": result.title if needs_title else state.session_title,
    }
