import ollama
import json
import time

def aggregator_node(state):
    t0 = time.time()
    structured_context = {
        "article": state.get("article", ""),
        "extracted_claims": state.get("claims", []),
        "classifier_signal": state.get("style_check", {}),
        "evidence_stances": state.get("stance_analysis", []),
        "source_credibility": state.get("source_credibility", [])[:5],
        "warnings": state.get("warnings", [])
    }
    
    img = state.get("image_result")
    if img and img.get("total_matches", 0) > 0:
        structured_context["image_check"] = img
        
    prompt = f"""You are a professional fact checker. Respond ONLY with valid JSON, no other text.
Do not invent facts. Base your verdict purely on the structured evidence below.

EVIDENCE BLOCK:
{json.dumps(structured_context, indent=2)}

Your task:
1. Review the classifier_signal.
2. Review the extracted_claims and evidence_stances. Do trusted sources CONTRADICT or SUPPORT the claims?
3. Calculate an overall verdict.
If major claims are CONTRADICTED by high credibility sources, the verdict is FAKE.
If major claims are SUPPORTED by high credibility sources, the verdict is REAL.
If evidence is missing, conflicting without a clear winner, or low credibility, the verdict is UNVERIFIED.

Respond with exactly this JSON structure:
{{
  "verdict": "FAKE" or "REAL" or "UNVERIFIED",
  "confidence": 0.9,
  "reasoning": "2-3 sentence explanation referencing specific evidence and source credibility"
}}
"""
    try:
        response = ollama.chat(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        parsed = json.loads(response["message"]["content"])
        final_verdict = parsed.get("verdict", "UNVERIFIED")
        confidence = float(parsed.get("confidence", 0.5))
        reasoning = parsed.get("reasoning", "")
        
    except Exception as e:
        # ADVANCED RULE-BASED FALLBACK
        stances = state.get("stance_analysis", [])
        cred_map = {s["url"]: s["credibility_score"] for s in state.get("source_credibility", [])}
        
        support_weight = 0
        contradict_weight = 0
        
        for stance in stances:
            url = stance.get("evidence_url")
            score = cred_map.get(url, 0.4)
            st = stance.get("stance")
            conf = stance.get("stance_confidence", 0.8)
            weighted = score * min(max(conf, 0.6), 1.0)
            
            if st == "SUPPORTS": support_weight += weighted
            elif st == "CONTRADICTS": contradict_weight += weighted
                
        if support_weight < 0.45 and contradict_weight < 0.45:
            final_verdict = "UNVERIFIED"
            confidence = 0.0
            reasoning = "Insufficient credible evidence found to verify the claims."
        else:
            margin = abs(support_weight - contradict_weight)
            if support_weight >= 0.60 and contradict_weight >= 0.60 and margin < 0.35:
                final_verdict = "UNVERIFIED"
                confidence = 0.0
                reasoning = "Conflicting credible evidence found."
            elif contradict_weight > support_weight:
                conf = min(0.70 + (contradict_weight * 0.20), 0.98)
                final_verdict = "FAKE"
                confidence = round(conf, 2)
                reasoning = f"Claims are contradicted by credible sources."
            elif support_weight > contradict_weight:
                conf = min(0.70 + (support_weight * 0.20), 0.98)
                final_verdict = "REAL"
                confidence = round(conf, 2)
                reasoning = f"Claims are supported by credible sources."
            else:
                final_verdict = "UNVERIFIED"
                confidence = 0.3
                reasoning = "Evidence is conflicting with equal weight."

    # ----- APPLY LOGIC CORRECTIONS BEFORE RETURNING -----
    classifier_signal = state.get("style_check", {})
    classifier_label = classifier_signal.get("label", "UNVERIFIED")
    classifier_conf = float(classifier_signal.get("confidence", 0.0))
    
    evidences = state.get("stance_analysis", [])
    cred_map = {s.get("url", ""): s.get("credibility_score", 0.0) for s in state.get("source_credibility", [])}
    
    # Recalculate weights strictly for the safety net
    s_weight = 0
    c_weight = 0
    max_support_conf = 0.0
    for e in evidences:
        st = str(e.get('stance')).upper()
        url = e.get("evidence_url", "")
        c_score = cred_map.get(url, 0.5)
        conf_score = float(e.get('stance_confidence', 0.5))
        w = c_score * conf_score
        
        if st == 'SUPPORTS':
            s_weight += w
            if conf_score > max_support_conf: max_support_conf = conf_score
        elif st == 'CONTRADICTS':
            c_weight += w

    # Safety Net 1: Evidence Void
    if len(evidences) == 0:
        final_verdict = 'UNVERIFIED'
        
    # Safety Net 2: The "Jupiter" Trap (Expected: FAKE, Got: REAL)
    # If the system thinks it's REAL, but the style classifier strongly warns it's FAKE
    elif final_verdict == 'REAL' and classifier_label == 'FAKE':
        if c_weight > 0.2:
            final_verdict = 'FAKE' # A fact checker contradicted it, trust the debunk
        elif max_support_conf < 0.85:
            final_verdict = 'UNVERIFIED' # Weak support for a fake-sounding claim
            
    # Safety Net 3: The "Obscure Claim" Trap (Expected: UNVERIFIED, Got: FAKE)
    # Don't call something FAKE just because of its writing style if there's no proof it's false
    elif final_verdict == 'FAKE':
        if c_weight < 0.5 and s_weight < 0.5 and classifier_conf < 0.99:
            final_verdict = 'UNVERIFIED'
        elif s_weight > 0.4 and c_weight > 0.4 and abs(s_weight - c_weight) < 0.5:
            final_verdict = 'UNVERIFIED' # Heavily conflicting evidence
            
    # Safety Net 4: The "Absurdity" Clause (Expected: FAKE, Got: UNVERIFIED)
    # The Sun is cold, etc. No evidence found because it's too absurd to debunk.
    elif final_verdict == 'UNVERIFIED' and classifier_label == 'FAKE' and classifier_conf > 0.98:
        if c_weight == 0 and s_weight == 0:
            final_verdict = 'FAKE'
            
    return {
        "final_verdict": final_verdict,
        "confidence": confidence,
        "reasoning": reasoning,
        "timing_aggregator": time.time()-t0
    }