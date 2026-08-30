import pytest
import numpy as np
from backend.app.ml.veritas_fusion import VeritasFusionEngine
from backend.app.ml.preprocessing import extract_linguistic_signals


def test_veritas_fusion_prediction():
    engine = VeritasFusionEngine()
    
    # Text embedding (384-d)
    text_emb = np.random.randn(384).astype(np.float32)
    text_emb /= np.linalg.norm(text_emb)

    fake_ling = extract_linguistic_signals(
        "BOMBSHELL REVELATION! SECRET MIRACLE CURE THEY DONT WANT YOU TO KNOW!",
        "SECRET MIRACLE"
    )

    retrieval_contra = {
        "max_contradicting_score": 0.85,
        "max_supporting_score": 0.05,
        "total_evidence_found": 3
    }

    result = engine.predict_multimodal(
        text_embedding=text_emb,
        linguistic_signals=fake_ling,
        retrieval_signals=retrieval_contra
    )

    assert result["verdict"] == "LIKELY_FAKE"
    assert result["calibrated_confidence"] >= 0.55
    assert result["evidence_strength"] in ("Strong", "Moderate")
    assert "modality_breakdown" in result
    assert result["modality_breakdown"]["text_percentage"] > 0
    assert len(result["key_reasons"]) >= 1
