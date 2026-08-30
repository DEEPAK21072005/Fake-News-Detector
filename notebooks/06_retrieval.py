"""
Notebook 06: Vector Retrieval & Stance Alignment Verification
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.retrieval.evidence_engine import evidence_engine
from backend.app.retrieval.narrative_engine import narrative_engine
from backend.app.retrieval.vector_store import vector_store

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 06: Vector Retrieval & Evidence Engine")
    print("=" * 60)

    print(f"Indexed documents in Vector Store: {vector_store.count()}")

    query = "Drinking coffee completely cures and prevents cancer."
    print(f"\nQuery Claim: '{query}'")

    res = evidence_engine.verify_claim(query, top_k=3)
    print(f"Evidence Strength: {res['evidence_strength']}")
    print(f"Max Contradicting Score: {res['max_contradicting_score']}")
    print(f"Max Supporting Score: {res['max_supporting_score']}")

    print("\nContradicting Evidence:")
    for c in res["contradicting_evidence"]:
        print(f"  [{c['source']}] {c['title']} (Sim: {c['similarity']:.3f}, Cred: {c['credibility_score']})")

    narr = narrative_engine.analyze_narrative_consistency(query)
    print(f"\nNarrative Consistency Distribution:")
    print(f"  Consistent: {narr['consistent_pct']*100:.1f}% | Contradictory: {narr['contradictory_pct']*100:.1f}% | Novel: {narr['novel_pct']*100:.1f}%")
    print(f"  Dominant: {narr['dominant_narrative']}")

if __name__ == "__main__":
    main()
