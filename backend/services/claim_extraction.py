import ollama
import json
import re

def extract_claims(article_text):
    prompt = f"""Extract verifiable factual claims. 
Decompose each claim into main_claim, entities, and qualifiers (like FIRST, ONLY, dates, numbers).
Return ONLY valid JSON in this format:
[
  {{
    "claim_id": 1, 
    "text": "Claim text", 
    "entities": ["Apollo 11", "Moon"],
    "qualifiers": ["FIRST", "July 1969"],
    "importance": 0.95
  }}
]
Text: {article_text}"""

    try:
        response = ollama.chat(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        parsed = json.loads(response["message"]["content"])
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed
    except Exception:
        pass
        
    # FALLBACK: Heuristic Claim Decomposition
    sentences = re.split(r'(?<=[.!?]) +', article_text)
    primary = sentences[0] if sentences else article_text[:200]
    
    qualifiers = []
    lower_text = primary.lower()
    
    # Simple regex for qualifiers
    if "first" in lower_text: qualifiers.append("FIRST")
    if "only" in lower_text: qualifiers.append("ONLY")
    if "never" in lower_text: qualifiers.append("NEVER")
    if "always" in lower_text: qualifiers.append("ALWAYS")
    
    # Match dates or years (e.g. 1969)
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', primary)
    qualifiers.extend(years)
    
    return [{
        "claim_id": 1, 
        "text": primary, 
        "entities": [],
        "qualifiers": list(set(qualifiers)),
        "importance": 1.0
    }]
