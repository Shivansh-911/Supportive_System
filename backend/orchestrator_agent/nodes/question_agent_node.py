from core.services.utils.logger import get_logger
from question_agent.graphs.question_graph import question_graph
from question_agent.states.question_agent_state import QuestionAgentState
from orchestrator_agent.states.orchestrator_state import OrchestratorAgentState

logger = get_logger(__name__)


def question_agent_node(state: OrchestratorAgentState) -> dict:
    

    if state.is_follow_up:
        last_qa_pair = state.last_qa_pair
    else:
        last_qa_pair = None

    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => delegating to question_agent with last QA pair %s", state.request_id,state.is_follow_up)
    qa_state = QuestionAgentState(
        request_id=state.request_id,
        question=state.rewritten_query,
        retrieval_filters={},
        last_qa_pair=last_qa_pair
    )

    result = question_graph.invoke(qa_state)

    logger.info("[REQUEST ID: %s] ORCHESTRATOR AGENT => question_agent returned answer", state.request_id)
    return {
        "response": result.get("answer") or "",
        "metadata": {
            "vector_chunks": [c.model_dump(mode="json") for c in (result.get("vector_hits") or [])],
            "bm25_chunks":   [c.model_dump(mode="json") for c in (result.get("bm25_hits") or [])],
            "fused_chunks":  [c.model_dump(mode="json") for c in (result.get("fused_candidates") or [])],
            "cited_chunks":  [c.model_dump(mode="json") for c in (result.get("cited_chunks") or [])],
        },
    }
    # return {
    #     "response": "Hello, world!",
    #     "metadata": {},
    # }