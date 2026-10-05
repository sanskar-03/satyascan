from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import warnings
from core.device import get_device

model_name = "cross-encoder/nli-deberta-v3-small"
tokenizer = None
model = None

def _load_model():
    global tokenizer, model
    if model is None:
        warnings.filterwarnings("ignore", category=FutureWarning)
        
        device = get_device()
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True)
        except Exception:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.to(device)
        model.eval()

import re

REFUTATION_SIGNALS = {
    'fake', 'false', 'hoax', 'debunk', 'debunked', 'debunks', 'myth', 'denied', 'denies',
    'misleading', 'untrue', 'refuted', 'refutes', 'discredited', 'disproven', 'contrary',
    'no evidence', 'cannot cure', 'never', 'unfounded', 'fabrication', 'fabricated',
    'rumor', 'rumours', 'rumour', 'conspiracy', 'scam', 'pseudoscience', 'bogus',
    'not true', 'incorrect', 'unsupported', 'disproved', 'did not', 'failed to'
}

AFFIRMATION_SIGNALS = {
    'won', 'win', 'wins', 'winner', 'winners', 'victory', 'victorious', 'champion', 'champions',
    'championship', 'title', 'defeated', 'defeat', 'beat', 'clinch', 'clinched', 'landed',
    'discovered', 'proved', 'proven', 'confirmed', 'verified', 'established', 'succeeded', 'first person'
}

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can", "can't", "cannot", "could", "did", "do", "does", "doing", "don't", "down", 
    "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", 
    "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", 
    "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", 
    "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "she", "should", "so", "some", "such", "than", "that", "the", "their", "theirs", 
    "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", 
    "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", 
    "while", "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves",
    "year", "years", "day", "days", "time", "times", "world", "light", "like", "well", "also",
    "many", "much", "part", "parts", "state", "states", "known", "called", "made", "used"
}

def extract_content_words(text):
    import re
    words = re.findall(r'[a-zA-Z0-9]{3,}', text.lower())
    return {w for w in words if w not in STOPWORDS}

def check_relevance(claim_text, evidence_text, qualifiers=None):
    if not evidence_text or len(evidence_text.strip()) < 15:
        return "LOW_RELEVANCE"
    c_words = extract_content_words(claim_text)
    e_words = extract_content_words(evidence_text)
    if len(c_words.intersection(e_words)) < 3:
        return "LOW_RELEVANCE"
    return "HIGH_RELEVANCE"

def select_best_sentence(claim, text):
    import re
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 15]
    if not sents:
        return text
    claim_words = extract_content_words(claim)
    scored = []
    for s in sents:
        s_words = extract_content_words(s)
        overlap = len(claim_words.intersection(s_words))
        scored.append((overlap, s))
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]

def detect_stance_batch(pairs):
    """
    Runs NLI efficiently in batches.
    pairs = [(claim_text, evidence_text, qualifiers), ...]
    Returns list of dicts.
    """
    _load_model()
    
    results = []
    valid_indices = []
    valid_pairs = []
    
    # Focused sentence extraction and relevance filtering
    for i, (claim_text, evidence_text, qualifiers) in enumerate(pairs):
        focused_evidence = select_best_sentence(claim_text, evidence_text)
        relevance = check_relevance(claim_text, focused_evidence, qualifiers)
        if relevance == "LOW_RELEVANCE":
            results.append({
                "stance": "NEUTRAL", 
                "confidence": 0.0,
                "relevance": relevance,
                "reason": "Evidence missed key qualifiers or entities."
            })
        else:
            results.append(None) # Placeholder
            valid_indices.append(i)
            valid_pairs.append((claim_text, focused_evidence))
            
    if not valid_pairs:
        return results
        
    # Batch NLI using torch
    device = get_device()
    batch_size = 16 if device.type == 'cuda' else 8
    
    for start_idx in range(0, len(valid_pairs), batch_size):
        batch = valid_pairs[start_idx : start_idx + batch_size]
        b_claims = [p[0] for p in batch]
        b_evidence = [p[1] for p in batch]
        
        inputs = tokenizer(b_evidence, b_claims, return_tensors="pt", truncation=True, max_length=512, padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.inference_mode():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
        for b_i, prob in enumerate(probs):
            contradiction = prob[0].item()
            entailment = prob[1].item()
            neutral = prob[2].item()
            
            stance = "NEUTRAL"
            conf = neutral
            
            if contradiction >= 0.55 and contradiction > entailment:
                stance = "CONTRADICTS"
                conf = contradiction
            elif entailment >= 0.55 and entailment > contradiction:
                stance = "SUPPORTS"
                conf = entailment
            elif contradiction >= 0.40 and contradiction > entailment + 0.15:
                stance = "CONTRADICTS"
                conf = contradiction
            elif entailment >= 0.40 and entailment > contradiction + 0.15:
                stance = "SUPPORTS"
                conf = entailment

            # Epistemic calibration: avoid false contradictions from tangential background snippets,
            # and detect strong semantic affirmations that NLI classifies as neutral.
            claim_text = b_claims[b_i]
            ev_text = b_evidence[b_i].lower()
            
            has_refutation = any(sig in ev_text for sig in REFUTATION_SIGNALS)
            
            if stance == "CONTRADICTS":
                if not has_refutation and not re.search(r'\b(not|never|no|neither|failed|untrue|false|lost|defeat(?:ed)? by)\b', ev_text):
                    stance = "NEUTRAL"
                    conf = 0.5
            elif stance == "NEUTRAL":
                c_words = set(re.findall(r'[a-zA-Z0-9]{3,}', claim_text.lower())) - STOPWORDS
                e_words = set(re.findall(r'[a-zA-Z0-9]{3,}', ev_text)) - STOPWORDS
                overlap = c_words.intersection(e_words)
                has_affirmation = any(sig in ev_text for sig in AFFIRMATION_SIGNALS)
                if len(overlap) >= 3 and has_affirmation and not has_refutation:
                    stance = "SUPPORTS"
                    conf = max(0.85, entailment + 0.5)
                
            orig_idx = valid_indices[start_idx + b_i]
            results[orig_idx] = {
                "stance": stance,
                "confidence": conf,
                "relevance": "HIGH_RELEVANCE",
                "raw_scores": {
                    "entailment": entailment,
                    "contradiction": contradiction,
                    "neutral": neutral
                }
            }
            
    return results

def detect_stance(claim_text, evidence_text, qualifiers=None):
    """Backwards compatibility for single items."""
    return detect_stance_batch([(claim_text, evidence_text, qualifiers)])[0]
