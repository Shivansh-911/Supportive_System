from langgraph.graph import END, START, StateGraph

from core.services.utils.logger import get_logger
from orchestrator_agent.nodes.classify_and_rewrite import classify_and_rewrite
from orchestrator_agent.nodes.create_session import create_session
from orchestrator_agent.nodes.llm_node import llm_node
from orchestrator_agent.nodes.load_history import load_history
from orchestrator_agent.nodes.question_agent_node import question_agent_node
from orchestrator_agent.states.orchestrator_state import OrchestratorAgentState

logger = get_logger(__name__)


def _route_session(state: OrchestratorAgentState) -> str:
    route = "load_history" if state.session_id is not None else "create_session"
    return route


def _route_intent(state: OrchestratorAgentState) -> str:
    return state.intent


def build_orchestrator_graph():
    builder = StateGraph(OrchestratorAgentState)

    builder.add_node("create_session", create_session)
    builder.add_node("load_history", load_history)
    builder.add_node("classify_and_rewrite", classify_and_rewrite)
    builder.add_node("question_agent_node", question_agent_node)
    builder.add_node("llm_node", llm_node)

    builder.add_conditional_edges(
        START,
        _route_session,
        {
            "create_session": "create_session",
            "load_history": "load_history",
        },
    )

    # New session: skip load_history, nothing to load
    builder.add_edge("create_session", "classify_and_rewrite")
    # Existing session: load history then classify
    builder.add_edge("load_history", "classify_and_rewrite")

    builder.add_conditional_edges(
        "classify_and_rewrite",
        _route_intent,
        {
            "question_agent": "question_agent_node",
            "llm": "llm_node",
        },
    )

    builder.add_edge("question_agent_node", END)
    builder.add_edge("llm_node", END)

    return builder.compile()


orchestrator_graph = build_orchestrator_graph()
