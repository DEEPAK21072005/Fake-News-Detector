"""
Notebook 04: Transformer Embedding & Semantic Representation Pipeline
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.ml.embeddings import get_embedding_provider

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 04: Transformer Semantic Representation")
    print("=" * 60)

    embedder = get_embedding_provider()
    print(f"Active Provider: {embedder.__class__.__name__} (Dimension: {embedder.dimension})")

    texts = [
        "Clinical trials confirm regular coffee consumption does not prevent cancer.",
        "Drinking three cups of coffee completely cures all stage 4 cancers.",
        "US Congress passes federal transportation budget."
    ]

    embs = embedder.embed_batch(texts)
    print(f"Generated embeddings shape: {embs.shape}")

    # Cosine similarities
    sim_0_1 = float(np.dot(embs[0], embs[1]))
    sim_0_2 = float(np.dot(embs[0], embs[2]))

    print(f"\nCosine Similarity [Coffee Fact vs Coffee Claim]: {sim_0_1:.4f}")
    print(f"Cosine Similarity [Coffee Fact vs Congress Budget]: {sim_0_2:.4f}")

if __name__ == "__main__":
    main()
