import pytest
import numpy as np
from backend.app.ml.embeddings import CompactTFIDFEmbeddingProvider, get_embedding_provider


def test_compact_tfidf_embedding():
    provider = CompactTFIDFEmbeddingProvider(n_components=128)
    vec = provider.embed_text("Economic indicators demonstrate moderate inflation growth.")
    assert len(vec) == 128
    # Norm should be close to 1
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 0.01


def test_embedding_batch():
    provider = get_embedding_provider()
    texts = [
        "International climate conference establishes emissions targets.",
        "Medical research study analyzes randomized pharmaceutical trial."
    ]
    batch_vecs = provider.embed_batch(texts)
    assert batch_vecs.shape[0] == 2
    assert batch_vecs.shape[1] == provider.dimension
