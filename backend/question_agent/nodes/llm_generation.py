from constants import TOP_K_CHUNKS_FOR_LLM
from core.services.utils.logger import get_logger
from question_agent.services.generation_service import GenerationService
from question_agent.services.llm_service import LLMService
from question_agent.states.question_agent_state import QuestionAgentState

logger = get_logger(__name__)

NO_CONTEXT_ANSWER = "I couldn't find relevant information to answer your question."


def llm_generation(state: QuestionAgentState) -> dict:
    top_chunks = state.fused_candidates[:TOP_K_CHUNKS_FOR_LLM]

    if not top_chunks:
        logger.warning("[REQUEST ID: %s] QUESTION AGENT => no chunks available for llm generation",state.request_id)
        return {"answer": NO_CONTEXT_ANSWER, "cited_chunks": []}

    logger.info("[REQUEST ID: %s] QUESTION AGENT => sending %d chunks to llm", state.request_id, len(top_chunks))
    last_qa_id = state.last_qa_pair.get("id") if state.last_qa_pair else None
    logger.info("[REQUEST ID: %s] QUESTION AGENT => for last question pair the [last_qa_id = %s]",state.request_id,last_qa_id)

    service = GenerationService(LLMService.get_model())
    answer, cited_chunks = service.generate(question=state.question, chunks=top_chunks, last_qa_pair=state.last_qa_pair)

    logger.info("[REQUEST ID: %s] QUESTION AGENT => llm generation produced answer [cited chunks = %d]",state.request_id,len(cited_chunks))

    return {"answer": answer, "cited_chunks": cited_chunks}
