from services.utils.logger import logger
import time
from services.classifier import classify
from services.retriever import search_news, search_news_for_claims
from services.image_search import reverse_image_search
from rag.ingest import query_trusted_sources
from services.claim_extraction import extract_claims
from services.stance_detection import detect_stance_batch
from urllib.parse import urlparse

CREDIBLE_DOMAINS = {
    # Fact-checking organizations
    "factcheck.org": 0.95, "fullfact.org": 0.95, "snopes.com": 0.95,
    "politifact.com": 0.95, "leadstories.com": 0.95, "truthorfiction.com": 0.95,
    "boomlive.in": 0.95, "altnews.in": 0.95, "checkyourfact.com": 0.95,
    # Wire services and international agencies
    "reuters.com": 0.95, "apnews.com": 0.95, "afp.com": 0.95,
    "bloomberg.com": 0.95, "upi.com": 0.90, "who.int": 0.95,
    # Major global broadcasters and newspapers
    "bbc.com": 0.92, "bbc.co.uk": 0.92, "theguardian.com": 0.90,
    "nytimes.com": 0.92, "washingtonpost.com": 0.90, "wsj.com": 0.92,
    "ft.com": 0.90, "economist.com": 0.90, "time.com": 0.88,
    "forbes.com": 0.85, "cnn.com": 0.88, "nbcnews.com": 0.88,
    "cbsnews.com": 0.88, "abcnews.go.com": 0.88, "npr.org": 0.92,
    "pbs.org": 0.92, "aljazeera.com": 0.88, "dw.com": 0.90,
    "france24.com": 0.88, "kyodonews.net": 0.90,
    # National news outlets
    "thehindu.com": 0.90, "indianexpress.com": 0.90, "hindustantimes.com": 0.85,
    "timesofindia.indiatimes.com": 0.85, "ndtv.com": 0.85, "indiatoday.in": 0.85,
    "news18.com": 0.82, "pib.gov.in": 0.95, "ddnews.gov.in": 0.92,
    "business-standard.com": 0.88, "livemint.com": 0.88,
    # Sports federations and reporting
    "icc-cricket.com": 0.95, "espn.com": 0.90, "espncricinfo.com": 0.92,
    "cricbuzz.com": 0.90, "fifa.com": 0.95, "olympics.com": 0.95,
    "uefa.com": 0.95, "nba.com": 0.95,
    # Science, space, nature, institutions
    "britannica.com": 0.95, "wikipedia.org": 0.80, "nasa.gov": 0.95,
    "esa.int": 0.95, "cern.ch": 0.95, "nature.com": 0.95, "science.org": 0.95,
    "scientificamerican.com": 0.92, "newscientist.com": 0.90, "nationalgeographic.com": 0.90,
    "smithsonianmag.com": 0.90, "livescience.com": 0.88, "phys.org": 0.88,
    "space.com": 0.88, "history.com": 0.85, "sciencedirect.com": 0.95,
    "usgs.gov": 0.95, "noaa.gov": 0.95, "weather.gov": 0.95, "fda.gov": 0.95,
    "audubon.org": 0.90,
    # Health and medicine
    "cdc.gov": 0.95, "nih.gov": 0.95, "un.org": 0.95, "loc.gov": 0.95,
    "mayoclinic.org": 0.95, "hopkinsmedicine.org": 0.95, "healthline.com": 0.85,
    "webmd.com": 0.85, "thelancet.com": 0.95, "nejm.org": 0.95, "bmj.com": 0.95
}

def _get_domain(url: str) -> str:
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        # Handle subdomains like en.wikipedia.org
        parts = domain.split('.')
        if len(parts) > 2 and parts[-2] not in ["co", "com", "gov", "org", "net", "ac", "edu"]:
            domain = ".".join(parts[-2:])
        elif len(parts) > 2: # e.g. co.uk
            domain = ".".join(parts[-3:])
        return domain
    except:
        return ""

def claim_extractor_node(state):
    """Extracts factual claims from the article."""
    t0 = time.time()
    try:
        claims = extract_claims(state["article"])
        return {"claims": claims, "timing_claim_ext": time.time()-t0}
    except Exception as e:
        return {"claims": [], "warnings": [f"Claim extraction failed: {str(e)}"], "timing_claim_ext": time.time()-t0}

def text_verifier_node(state):
    t0 = time.time()
    try:
        result = classify(state["article"], title=state.get("title", ""))
        return {"style_check": result, "timing_text_ver": time.time()-t0}
    except Exception as e:
        return {"style_check": {"label": "UNVERIFIED", "confidence": 0.0}, "warnings": [f"Classifier failed: {str(e)}"], "timing_text_ver": time.time()-t0}

def image_verifier_node(state):
    t0 = time.time()
    if not state.get("image_url"):
        return {"image_result": None, "timing_image_ver": time.time()-t0}
    try:
        result = reverse_image_search(state["image_url"])
        return {"image_result": result, "timing_image_ver": time.time()-t0}
    except Exception as e:
        return {"image_result": None, "warnings": [f"Image verification failed: {str(e)}"], "timing_image_ver": time.time()-t0}

def fact_check_retriever_node(state):
    t0 = time.time()
    claims = state.get("claims", [])
    
    if claims:
        live = search_news_for_claims(claims)
        trusted = []
        seen_urls = set()
        for c in claims:
            try:
                res = query_trusted_sources(c.get("text", ""))
                for r in res:
                    u = r.get("url")
                    if u not in seen_urls:
                        seen_urls.add(u)
                        r["claim_id"] = c.get("claim_id")
                        trusted.append(r)
            except Exception as e:
                logger.error(f"An error occurred: {e}", exc_info=True)
    else:
        query = state["article"][:200]
        try:
            live = search_news(query)
        except Exception as e:
            logger.error(f"Fallback news search failed for query '{query}': {str(e)}", exc_info=True)
            live = []
        try:
            trusted = query_trusted_sources(query)
        except Exception as e:
            logger.error(f"Fallback trusted source search failed for query '{query}': {str(e)}", exc_info=True)
            trusted = []

    return {"live_evidence": live, "trusted_evidence": trusted, "timing_retriever": time.time()-t0}

def stance_detection_node(state):
    """Calculates stance using BATcH NLI for each claim and evidence."""
    t0 = time.time()
    claims = state.get("claims", [])
    all_evidence = state.get("live_evidence", []) + state.get("trusted_evidence", [])
    
    try:
        pairs = []
        mapping = [] # to keep track of claim_id and url
        
        if not claims:
            main_claim = state["article"][:200]
            seen_u = set()
            for ev in all_evidence:
                u = ev.get("url")
                if u in seen_u:
                    continue
                seen_u.add(u)
                snippet = ev.get("snippet") or ev.get("content", "")
                if snippet:
                    pairs.append((main_claim, snippet, []))
                    mapping.append((None, u))
        else:
            for c in claims:
                claim_text = c.get("text", "")
                claim_id = c.get("claim_id")
                qualifiers = c.get("qualifiers", [])
                
                relevant_ev = [ev for ev in all_evidence if ev.get("claim_id") == claim_id or "claim_id" not in ev]
                seen_u = set()
                for ev in relevant_ev[:30]: # Up to 30 sources per claim for deep live testing
                    u = ev.get("url")
                    if u in seen_u:
                        continue
                    seen_u.add(u)
                    snippet = ev.get("snippet") or ev.get("content", "")
                    if snippet:
                        pairs.append((claim_text, snippet, qualifiers))
                        mapping.append((claim_id, u))
                        
        if not pairs:
            return {"stance_analysis": [], "timing_stance": time.time()-t0}
            
        # Batch inference
        batch_results = detect_stance_batch(pairs)
        
        stance_results = []
        for i, res in enumerate(batch_results):
            cid, url = mapping[i]
            stance_results.append({
                "claim_id": cid,
                "evidence_url": url,
                "stance": res["stance"],
                "stance_confidence": res["confidence"]
            })
                    
        return {"stance_analysis": stance_results, "timing_stance": time.time()-t0}
    except Exception as e:
        return {"stance_analysis": [], "warnings": [f"Stance detection failed: {str(e)}"], "timing_stance": time.time()-t0}

def source_credibility_node(state):
    t0 = time.time()
    scored = []

    for item in (state.get("trusted_evidence") or []):
        url = item.get("url", "")
        domain = _get_domain(url)
        domain_score = CREDIBLE_DOMAINS.get(domain)
        if domain_score is None:
            if domain.endswith(".gov") or domain.endswith(".edu") or domain.endswith(".int") or domain.endswith(".org"):
                domain_score = 0.95
            else:
                domain_score = 0.85
        scored.append({"url": url, "credibility_score": domain_score})

    for item in (state.get("live_evidence") or []):
        url = item.get("url", "")
        domain = _get_domain(url)
        domain_score = CREDIBLE_DOMAINS.get(domain)
        if domain_score is None:
            if any(domain.endswith(tld) for tld in [".gov", ".edu", ".ac.uk", ".gov.in", ".gov.uk", ".mil", ".int"]):
                domain_score = 0.95
            elif domain.endswith(".org"):
                domain_score = 0.85
            elif any(sub in domain for sub in ["news", "times", "post", "tribune", "chronicle", "herald", "gazette", "daily", "press", "journal", "today", "report", "cric", "sport", "tv", "media"]):
                domain_score = 0.85
            else:
                domain_score = 0.75
        scored.append({"url": url, "credibility_score": domain_score})

    scored.sort(key=lambda x: -x["credibility_score"])
    
    seen = set()
    deduped = []
    for s in scored:
        if s["url"] not in seen:
            seen.add(s["url"])
            deduped.append(s)
            
    return {"source_credibility": deduped, "timing_credibility": time.time()-t0}