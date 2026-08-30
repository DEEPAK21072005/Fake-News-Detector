import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.core.logging_config import logger
from backend.app.ml.embeddings import get_embedding_provider
from backend.app.retrieval.vector_store import vector_store


class NarrativeEngine:
    """
    Narrative Consistency & Semantic Novelty Engine.
    Evaluates how closely submitted claims match existing verified or debunked narrative clusters.
    """
    def __init__(self):
        self.embedding_provider = get_embedding_provider()

    def analyze_narrative_consistency(self, claim_text: str) -> Dict[str, Any]:
        """
        Calculates exact narrative distribution:
          - Consistent %: claim aligns with established credible reporting.
          - Contradictory %: claim matches known debunked or disputed narratives.
          - Novel/Unknown %: claim has low semantic overlap with indexed narrative corpus.
        """
        if not claim_text.strip() or vector_store.count() == 0:
            return {
                "consistent_pct": 0.33,
                "contradictory_pct": 0.33,
                "novel_pct": 0.34,
                "dominant_narrative": "Unindexed / Novel Content",
                "similarity_spread": 0.0,
                "similar_narratives": []
            }

        query_emb = self.embedding_provider.embed_text(claim_text)
        top_matches = vector_store.search(query_emb, top_k=6)

        if not top_matches:
            return {
                "consistent_pct": 0.10,
                "contradictory_pct": 0.10,
                "novel_pct": 0.80,
                "dominant_narrative": "Novel Narrative (No Prior Matches)",
                "similarity_spread": 0.0,
                "similar_narratives": []
            }

        # Compute narrative stance mass
        support_mass = 0.0
        contradict_mass = 0.0
        max_sim = 0.0

        for match in top_matches:
            sim = max(0.0, match.get("similarity", 0.0))
            max_sim = max(max_sim, sim)
            stance = str(match.get("stance_tag", "")).lower()
            if "contradict" in stance or "debunk" in stance or "fake" in stance:
                contradict_mass += sim * 1.5
            elif "support" in stance or "confirm" in stance:
                support_mass += sim * 1.5
            else:
                support_mass += sim * 0.5
                contradict_mass += sim * 0.5

        # Novelty is inversely proportional to maximum match similarity
        novel_mass = max(0.1, (1.0 - max_sim) * 2.0)
        total_mass = support_mass + contradict_mass + novel_mass

        p_consistent = round(float(support_mass / total_mass), 2)
        p_contradictory = round(float(contradict_mass / total_mass), 2)
        p_novel = round(float(1.0 - (p_consistent + p_contradictory)), 2)
        p_novel = max(0.0, p_novel)

        # Normalize to 100%
        sum_p = p_consistent + p_contradictory + p_novel
        p_consistent = round(p_consistent / sum_p, 2)
        p_contradictory = round(p_contradictory / sum_p, 2)
        p_novel = round(1.0 - (p_consistent + p_contradictory), 2)

        if p_contradictory > p_consistent and p_contradictory > p_novel:
            dominant = "Contradicts Established Reporting"
        elif p_consistent > p_contradictory and p_consistent > p_novel:
            dominant = "Consistent with Credible Sources"
        else:
            dominant = "Novel or Emerging Narrative"

        return {
            "consistent_pct": p_consistent,
            "contradictory_pct": p_contradictory,
            "novel_pct": p_novel,
            "dominant_narrative": dominant,
            "similarity_spread": round(float(max_sim), 3),
            "similar_narratives": [
                {
                    "title": m.get("title"),
                    "source": m.get("source"),
                    "similarity": m.get("similarity"),
                    "stance": m.get("stance_tag")
                }
                for m in top_matches[:3]
            ]
        }


narrative_engine = NarrativeEngine()
