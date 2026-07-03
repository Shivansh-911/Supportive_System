from langgraph.graph import END, START, StateGraph

from question_agent.nodes.bm25_search import bm25_search
from question_agent.nodes.embed_query import embed_query
from question_agent.nodes.llm_generation import llm_generation
from question_agent.nodes.rrf_fusion import rrf_fusion
from question_agent.nodes.vector_search import vector_search
from question_agent.states.question_agent_state import QuestionAgentState


def build_question_graph():
    builder = StateGraph(QuestionAgentState)

    builder.add_node('embed_query', embed_query)
    builder.add_node('vector_search', vector_search)
    builder.add_node('bm25_search', bm25_search)
    builder.add_node('rrf_fusion', rrf_fusion)
    builder.add_node('llm_generation', llm_generation)

    builder.add_edge(START, 'embed_query')
    # Fan out: vector + bm25 run in parallel off the same query_vector.
    builder.add_edge('embed_query', 'vector_search')
    builder.add_edge('embed_query', 'bm25_search')
    # Fan in: rrf_fusion waits for both searches before running.
    builder.add_edge('vector_search', 'rrf_fusion')
    builder.add_edge('bm25_search', 'rrf_fusion')
    builder.add_edge('rrf_fusion', 'llm_generation')
    builder.add_edge('llm_generation', END)

    return builder.compile()


question_graph = build_question_graph()
