"""
Notebook 07: VeritasFusion Multimodal Architecture & Calibration
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.ml.veritas_fusion import VeritasFusionEngine
from backend.app.ml.preprocessing import extract_linguistic_signals

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 07: VeritasFusion Multimodal Engine")
    print("=" * 60)

    engine = VeritasFusionEngine()
    print(f"Fusion Strategy: {engine.fusion_strategy}")
    print(f"Modality Weights: {engine.base_weights}")

    # Simulated multimodal inputs
    dummy_text_emb = np.random.randn(384).astype(np.float32)
    dummy_text_emb /= np.linalg.norm(dummy_text_emb)

    dummy_ling = extract_linguistic_signals("SHOCKING REVELATION: SECRET MIRACLE CURE!", "SECRET CURE")
    dummy_ret = {
        "max_contradicting_score": 0.82,
        "max_supporting_score": 0.10,
        "total_evidence_found": 2
    }
    dummy_narr = {
        "consistent_pct": 0.10,
        "contradictory_pct": 0.85,
        "novel_pct": 0.05
    }

    result = engine.predict_multimodal(
        text_embedding=dummy_text_emb,
        linguistic_signals=dummy_ling,
        retrieval_signals=dummy_ret,
        narrative_signals=dummy_narr
    )

    print("\n--- VeritasFusion Output ---")
    print(f"Verdict: {result['verdict']}")
    print(f"Calibrated Confidence: {result['calibrated_confidence']:.2f}")
    print(f"Evidence Strength: {result['evidence_strength']}")
    print(f"Reliability: {result['reliability']}")
    print(f"Modality Breakdown: {result['modality_breakdown']}")
    print(f"Key Reasons: {result['key_reasons']}")

if __name__ == "__main__":
    main()
