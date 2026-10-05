from services.graph import verification_graph

def verify_news(article, image_url=None):
    initial_state = {
        "article": article,
        "image_url": image_url,
    }

    import time
    from core.device import get_device_name, get_device
    
    t0 = time.time()
    result = verification_graph.invoke(initial_state)
    elapsed_ms = int((time.time() - t0) * 1000)

    # Note: RAG and page fetch are combined in timing_retriever in our current implementation.
    retriever_ms = int(result.get("timing_retriever", 0) * 1000)
    
    return {
        "final_verdict": result.get("final_verdict"),
        "confidence": result.get("confidence"),
        "reasoning": result.get("reasoning"),
        "live_evidence": result.get("live_evidence"),
        "trusted_evidence": result.get("trusted_evidence"),
        "source_credibility": result.get("source_credibility"),
        "claims": result.get("claims", []),
        "stance_analysis": result.get("stance_analysis", []),
        "image_verification": result.get("image_result"),
        "_debug_style_classifier": result.get("style_check"),
        "processing_time_ms": elapsed_ms,
        "timings": {
            "claim_extraction_ms": int(result.get("timing_claim_ext", 0) * 1000),
            "web_search_ms": retriever_ms,
            "rag_ms": retriever_ms,
            "page_fetch_ms": retriever_ms,
            "nli_ms": int(result.get("timing_stance", 0) * 1000),
            "verdict_ms": int(result.get("timing_aggregator", 0) * 1000),
            "llm_ms": int(result.get("timing_aggregator", 0) * 1000)
        },
        "hardware": {
            "device": get_device().type,
            "gpu": get_device_name()
        }
    }