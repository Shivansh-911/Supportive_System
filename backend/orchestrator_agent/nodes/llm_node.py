from langchain_core.messages import HumanMessage, SystemMessage

from core.services.utils.logger import get_logger
from orchestrator_agent.services.llm_service import LLMService
from orchestrator_agent.services.prompts.llm_node_prompt import SYSTEM
from orchestrator_agent.states.orchestrator_state import OrchestratorAgentState

logger = get_logger(__name__)


def llm_node(state: OrchestratorAgentState) -> dict:
    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => llm_node invoked", state.request_id)
    model = LLMService.get_model()
    result = model.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=state.rewritten_query),
    ])
    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => llm_node completed]", state.request_id)
    return {"response": result.content, "metadata": {}}
