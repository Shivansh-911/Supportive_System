from core.services.utils.logger import get_logger
from orchestrator_agent.models.message import Message
from orchestrator_agent.models.session import Session
from orchestrator_agent.states.orchestrator_state import OrchestratorAgentState

logger = get_logger(__name__)


def load_history(state: OrchestratorAgentState) -> dict:
    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => loading history for [session_id=%s]", state.request_id, state.session_id)
    last_message = Message.objects.get_last_message(state.session_id)

    last_qa_pair = None
    if last_message:
        last_qa_pair = {
            "id": last_message.request_id,
            "question": last_message.raw_query,
            "rewritten_query": last_message.rewritten_query,
            "answer": last_message.raw_answer,
            "intent": last_message.intent,
        }
        logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => history loaded with last message", state.request_id)
    else:
        logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => no history found for session", state.request_id)

    session = Session.objects.get_session(state.session_id)

    return {"last_qa_pair": last_qa_pair, "session_title": session.title}
