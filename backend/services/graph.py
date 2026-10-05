from langgraph.graph import StateGraph, START, END
from services.graph_state import VerificationState
from services.agents import (
    text_verifier_node,
    image_verifier_node,
    claim_extractor_node,
    fact_check_retriever_node,
    source_credibility_node,
    stance_detection_node,
)
from services.llm import aggregator_node

def build_verification_graph():
    graph = StateGraph(VerificationState)

    # Add all nodes
    graph.add_node("claim_extractor", claim_extractor_node)
    graph.add_node("text_verifier", text_verifier_node)
    graph.add_node("image_verifier", image_verifier_node)
    
    graph.add_node("fact_check_retriever", fact_check_retriever_node)
    graph.add_node("stance_detection", stance_detection_node)
    graph.add_node("source_credibility", source_credibility_node)
    
    graph.add_node("aggregator", aggregator_node)

    # Phase 1: Parallel initial processing
    graph.add_edge(START, "claim_extractor")
    graph.add_edge(START, "text_verifier")
    graph.add_edge(START, "image_verifier")

    # Phase 2: Retrieval depends on claims
    graph.add_edge("claim_extractor", "fact_check_retriever")

    # Phase 3: Stance and Credibility depend on retrieved evidence
    graph.add_edge("fact_check_retriever", "stance_detection")
    graph.add_edge("fact_check_retriever", "source_credibility")

    # Phase 4: Aggregator runs when final parallel branches complete.
    graph.add_edge(["text_verifier", "image_verifier", "stance_detection", "source_credibility"], "aggregator")

    graph.add_edge("aggregator", END)

    return graph.compile()

verification_graph = build_verification_graph()