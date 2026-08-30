import pytest
import numpy as np
from backend.app.retrieval.vector_store import LocalVectorStore
from backend.app.retrieval.evidence_engine import EvidenceEngine
from backend.app.retrieval.narrative_engine import NarrativeEngine


def test_vector_store_operations(tmp_path):
    store = LocalVectorStore(storage_path=tmp_path / "test_index.joblib")
    
    docs = [
        {"id": 1, "title": "Coffee does not cure cancer", "stance_tag": "Contradicting", "category": "Health"},
        {"id": 2, "title": "Senate passes transportation infrastructure bill", "stance_tag": "Supporting", "category": "Politics"}
    ]
    # Synthetic vectors
    emb = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0]
    ], dtype=np.float32)

    store.add_documents(docs, emb)
    assert store.count() == 2

    # Query matching doc 1
    query = np.array([0.9, 0.1, 0.0, 0.0], dtype=np.float32)
    results = store.search(query, top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["similarity"] > 0.8


def test_narrative_engine():
    engine = NarrativeEngine()
    res = engine.analyze_narrative_consistency("Clinical research confirms health benefits.")
    assert "consistent_pct" in res
    assert "contradictory_pct" in res
    assert "novel_pct" in res
    total_pct = res["consistent_pct"] + res["contradictory_pct"] + res["novel_pct"]
    assert abs(total_pct - 1.0) < 0.02
