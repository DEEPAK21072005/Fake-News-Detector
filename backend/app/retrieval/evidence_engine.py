import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.core.logging_config import logger
from backend.app.ml.embeddings import get_embedding_provider
from backend.app.retrieval.vector_store import vector_store


DOMAIN_CREDIBILITY_MAP = {
    "reuters.com": 0.96,
    "apnews.com": 0.96,
    "bbc.com": 0.94,
    "snopes.com": 0.95,
    "politifact.com": 0.95,
    "factcheck.org": 0.94,
    "nature.com": 0.98,
    "sciencedaily.com": 0.93,
    "who.int": 0.98,
    "cdc.gov": 0.98,
    "theguardian.com": 0.90,
    "nytimes.com": 0.90,
    "washingtonpost.com": 0.90,
}


class EvidenceEngine:
    """
    Evidence Retrieval & Stance Alignment Engine.
    Distinguishes factual support from contradiction and incorporates source authority.
    """
    def __init__(self):
        self.embedding_provider = get_embedding_provider()

    def verify_claim(self, claim_text: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Search evidence database, evaluate stance, and compute evidence polarity.
        """
        if not claim_text.strip():
            return {
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "related_evidence": [],
                "max_supporting_score": 0.0,
                "max_contradicting_score": 0.0,
                "net_evidence_polarity": 0.0,
                "total_evidence_found": 0,
                "evidence_strength": "None"
            }

        # 1. Generate claim dense embedding
        query_emb = self.embedding_provider.embed_text(claim_text)

        # 2. Vector search top-k matching evidence
        raw_matches = vector_store.search(query_emb, top_k=top_k)

        supporting = []
        contradicting = []
        related = []

        for item in raw_matches:
            similarity = item.get("similarity", 0.0)
            if similarity < 0.25:
                continue

            # Lookup domain credibility
            domain = item.get("domain", "").lower()
            cred_weight = DOMAIN_CREDIBILITY_MAP.get(domain, item.get("credibility_score", 0.80))
            adjusted_score = round(similarity * cred_weight, 4)

            evidence_entry = {
                "id": item.get("id"),
                "title": item.get("title"),
                "text": item.get("text"),
                "source": item.get("source"),
                "url": item.get("url"),
                "publication_date": item.get("publication_date"),
                "domain": domain or item.get("source", ""),
                "similarity": similarity,
                "credibility_score": cred_weight,
                "adjusted_score": adjusted_score,
                "stance": item.get("stance_tag", "Supporting"),
                "category": item.get("category", "General")
            }

            stance = str(item.get("stance_tag", "")).lower()
            if "contradict" in stance or "debunk" in stance or "fake" in stance:
                contradicting.append(evidence_entry)
            elif "support" in stance or "confirm" in stance or "true" in stance:
                supporting.append(evidence_entry)
            else:
                related.append(evidence_entry)

        max_support = max([e["adjusted_score"] for e in supporting], default=0.0)
        max_contradict = max([e["adjusted_score"] for e in contradicting], default=0.0)
        net_polarity = round(max_contradict - max_support, 4)
        total_found = len(supporting) + len(contradicting) + len(related)

        if total_found >= 3 and (max_support > 0.65 or max_contradict > 0.65):
            strength = "Strong"
        elif total_found >= 1 and (max_support > 0.45 or max_contradict > 0.45):
            strength = "Moderate"
        elif total_found > 0:
            strength = "Weak"
        else:
            strength = "None"

        return {
            "supporting_evidence": supporting,
            "contradicting_evidence": contradicting,
            "related_evidence": related,
            "max_supporting_score": max_support,
            "max_contradicting_score": max_contradict,
            "net_evidence_polarity": net_polarity,
            "total_evidence_found": total_found,
            "evidence_strength": strength
        }


evidence_engine = EvidenceEngine()
