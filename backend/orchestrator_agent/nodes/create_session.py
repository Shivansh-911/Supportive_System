from core.services.utils.logger import get_logger
from orchestrator_agent.models.session import Session
from orchestrator_agent.states.orchestrator_state import OrchestratorAgentState

logger = get_logger(__name__)


def create_session(state: OrchestratorAgentState) -> dict:
    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => creating new session", state.request_id)
    session = Session.objects.create_session(user_id=state.user_id)
    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => session created [session_id=%s]", state.request_id, session.id)
    return {"session_id": session.id}
