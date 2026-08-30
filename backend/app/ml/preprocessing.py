import re
import string
import math
from typing import Dict, Any, List, Tuple


SENSATIONAL_KEYWORDS = {
    "shocking", "unbelievable", "bombshell", "exposed", "secret", "miracle", "banned",
    "mainstream media", "they don't want you to know", "proof", "conspiracy", "hidden truth",
    "mind-blowing", "urgent", "must see", "devastating", "catastrophic", "traitor",
    "hoax", "coverup", "scandalous", "guaranteed", "plot", "deep state", "crisis", "outrage"
}

CLICKBAIT_PATTERNS = [
    r"you won't believe",
    r"what happens next",
    r"this is why",
    r"the reason why",
    r"\d+\s+(things|ways|secrets|reasons|facts)",
    r"will blow your mind",
    r"warning:",
    r"alert:",
    r"revealed:"
]

POSITIVE_LEXICON = {
    "good", "great", "excellent", "positive", "success", "proven", "benefit", "breakthrough",
    "reliable", "confirmed", "true", "accurate", "official", "verified", "supported", "peace"
}

NEGATIVE_LEXICON = {
    "bad", "terrible", "fake", "hoax", "false", "destroy", "ruin", "crisis", "danger",
    "deadly", "fatal", "scam", "corrupt", "failure", "threat", "disaster", "toxic", "lie"
}


def clean_text_basic(text: str) -> str:
    """Clean text for tokenizers and classical models."""
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_tokens(text: str) -> List[str]:
    """Tokenize and lower-case text."""
    cleaned = clean_text_basic(text).lower()
    return re.findall(r'\b[a-z0-9_]+\b', cleaned)


def extract_linguistic_signals(text: str, title: str = "") -> Dict[str, Any]:
    """
    Extract multi-dimensional linguistic, stylistic, and emotional signals.
    Computes exact numerical metrics for sensationalism, clickbait, stylometry, and sentiment.
    """
    full_text = f"{title} {text}".strip() if title else text.strip()
    if not full_text:
        return {
            "sensationalism_score": 0.0,
            "clickbait_score": 0.0,
            "uppercase_ratio": 0.0,
            "punctuation_anomaly_score": 0.0,
            "sentiment_polarity": 0.0,
            "emotional_intensity": 0.0,
            "lexical_diversity_ttr": 0.0,
            "average_sentence_length": 0.0,
            "total_words": 0,
            "total_sentences": 0,
            "clickbait_indicators_found": [],
            "sensational_keywords_found": []
        }

    tokens = normalize_tokens(full_text)
    total_words = len(tokens)
    unique_words = len(set(tokens))
    lexical_diversity = round(unique_words / total_words, 4) if total_words > 0 else 0.0

    # Sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', full_text) if s.strip()]
    total_sentences = max(len(sentences), 1)
    avg_sentence_len = round(total_words / total_sentences, 2)

    # Uppercase analysis (all-caps words)
    raw_words = re.findall(r'\b[A-Za-z]+\b', full_text)
    uppercase_words = [w for w in raw_words if len(w) > 1 and w.isupper()]
    uppercase_ratio = round(len(uppercase_words) / max(len(raw_words), 1), 4)

    # Exclamation & Question Marks anomaly
    exclamations = full_text.count("!")
    questions = full_text.count("?")
    multi_punct = len(re.findall(r'[!?]{2,}', full_text))
    punctuation_score = round(min(1.0, (exclamations * 1.5 + questions + multi_punct * 3) / max(total_sentences * 2, 5)), 4)

    # Sensationalism
    found_sensational = [w for w in tokens if w in SENSATIONAL_KEYWORDS]
    # Check multi-word sensational phrases
    full_lower = full_text.lower()
    for phrase in ["mainstream media", "they don't want you to know", "hidden truth", "deep state"]:
        if phrase in full_lower and phrase not in found_sensational:
            found_sensational.append(phrase)
    sensationalism_score = round(min(1.0, len(found_sensational) / max(total_words * 0.05, 3.0)), 4)

    # Clickbait
    found_clickbait = []
    for pattern in CLICKBAIT_PATTERNS:
        if re.search(pattern, full_lower):
            found_clickbait.append(pattern)
    if title and (title.endswith("?") or title.isupper()):
        found_clickbait.append("title_exaggeration")
    clickbait_score = round(min(1.0, (len(found_clickbait) * 0.25) + (uppercase_ratio * 0.5)), 4)

    # Sentiment & Emotional Intensity
    pos_count = sum(1 for w in tokens if w in POSITIVE_LEXICON)
    neg_count = sum(1 for w in tokens if w in NEGATIVE_LEXICON)
    sentiment_polarity = round((pos_count - neg_count) / max(pos_count + neg_count, 1), 4)
    emotional_intensity = round(min(1.0, (pos_count + neg_count + len(found_sensational)) / max(total_words * 0.1, 4.0)), 4)

    return {
        "sensationalism_score": sensationalism_score,
        "clickbait_score": clickbait_score,
        "uppercase_ratio": uppercase_ratio,
        "punctuation_anomaly_score": punctuation_score,
        "sentiment_polarity": sentiment_polarity,
        "emotional_intensity": emotional_intensity,
        "lexical_diversity_ttr": lexical_diversity,
        "average_sentence_length": avg_sentence_len,
        "total_words": total_words,
        "total_sentences": total_sentences,
        "clickbait_indicators_found": found_clickbait[:5],
        "sensational_keywords_found": list(set(found_sensational))[:8]
    }


def extract_claims(text: str, title: str = "", max_claims: int = 4) -> List[Dict[str, Any]]:
    """
    Extract factual claims and assertions from text.
    Uses syntactic sentence analysis, declarative verb structures, and assertion heuristics.
    """
    full_text = f"{title}. {text}" if title else text
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', full_text) if len(s.strip()) > 20]
    
    claims = []
    # If title exists, treat title as primary claim candidate
    if title and len(title.strip()) > 10:
        claims.append({
            "claim_id": 1,
            "text": title.strip(),
            "confidence": 0.92,
            "is_title_claim": True,
            "type": "Primary Headline Assertion"
        })

    # Filter declarative factual assertions
    claim_markers = ["discovered", "reported", "claims", "revealed", "announced", "found", "stated", "confirmed", "prevent", "causes", "passed", "won", "arrested"]
    
    for s in sentences:
        if len(claims) >= max_claims:
            break
        s_clean = s.strip()
        # Skip if identical to title
        if title and s_clean.lower() in title.lower():
            continue
        
        # Check for claim markers or strong declarative patterns
        has_marker = any(m in s_clean.lower() for m in claim_markers)
        has_numbers_or_entities = bool(re.search(r'\d+', s_clean)) or bool(re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', s_clean))
        
        if has_marker or (has_numbers_or_entities and len(s_clean) > 35):
            claims.append({
                "claim_id": len(claims) + 1,
                "text": s_clean,
                "confidence": 0.85 if has_marker else 0.72,
                "is_title_claim": False,
                "type": "Extracted Proposition"
            })

    if not claims and sentences:
        claims.append({
            "claim_id": 1,
            "text": sentences[0],
            "confidence": 0.65,
            "is_title_claim": False,
            "type": "Leading Assertion"
        })

    return claims
