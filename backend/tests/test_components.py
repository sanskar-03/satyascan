import pytest
from services.agents import _get_domain
from services.classifier import classify
from services.claim_extraction import extract_claims
from services.stance_detection import detect_stance

def test_domain_parsing():
    assert _get_domain("https://www.reuters.com/article/123") == "reuters.com"
    assert _get_domain("http://bbc.com/news") == "bbc.com"
    assert _get_domain("invalid_url") == ""
    assert _get_domain("https://reuters.com.fake.site/news") == "reuters.com.fake.site"

def test_long_article_handling():
    # Provide a string much longer than 512 tokens
    long_text = "word " * 1000
    res = classify(long_text, "Test Title")
    assert "label" in res
    assert "confidence" in res

def test_missing_evidence_fallback():
    from services.llm import aggregator_node
    state = {
        "article": "Claim without evidence",
        "stance_analysis": []
    }
    # With ollama unavailable, it should fallback to UNVERIFIED
    res = aggregator_node(state)
    assert res["final_verdict"] == "UNVERIFIED"

def test_evidence_stance():
    # nli-deberta-v3-small testing
    res = detect_stance("A normal human heart has four chambers.", "The heart is divided into four chambers.")
    assert res["stance"] in ["SUPPORTS", "NEUTRAL", "CONTRADICTS"]

def test_claim_extraction_fallback():
    # if Ollama is off, it should fallback to returning the first 200 chars
    res = extract_claims("This is a short article about space.")
    assert len(res) > 0
    assert "text" in res[0]
