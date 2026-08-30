import re
import numpy as np
from typing import List, Dict, Any, Callable


def chunk_document(
    text: str,
    max_tokens_per_chunk: int = 256,
    overlap_tokens: int = 32
) -> List[Dict[str, Any]]:
    """
    Intelligent sentence-preserving document chunking.
    Prevents truncation and avoids token explosion on long articles.
    """
    if not text or not text.strip():
        return []

    # Split into sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if not sentences:
        sentences = [text.strip()]

    chunks = []
    current_sentences = []
    current_word_count = 0

    for sentence in sentences:
        words = sentence.split()
        sentence_word_count = len(words)

        if current_word_count + sentence_word_count > max_tokens_per_chunk and current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append({
                "chunk_index": len(chunks),
                "text": chunk_text,
                "token_count": current_word_count,
            })
            # Overlap: keep last sentence if possible
            if len(current_sentences) > 1 and overlap_tokens > 0:
                current_sentences = [current_sentences[-1]]
                current_word_count = len(current_sentences[0].split())
            else:
                current_sentences = []
                current_word_count = 0

        current_sentences.append(sentence)
        current_word_count += sentence_word_count

    if current_sentences:
        chunk_text = " ".join(current_sentences)
        chunks.append({
            "chunk_index": len(chunks),
            "text": chunk_text,
            "token_count": current_word_count,
        })

    return chunks


def aggregate_chunk_embeddings(
    chunk_embeddings: np.ndarray,
    pooling: str = "attention_mean"
) -> np.ndarray:
    """
    Hierarchical aggregation of chunk embeddings.
    Combines chunk vectors into a document vector using weighted importance.
    """
    if len(chunk_embeddings) == 0:
        return np.zeros(384, dtype=np.float32)
    if len(chunk_embeddings) == 1:
        return chunk_embeddings[0]

    if pooling == "mean":
        return np.mean(chunk_embeddings, axis=0)
    elif pooling == "max":
        return np.max(chunk_embeddings, axis=0)
    else:
        # Attention-like weighting: first chunk (headline/lead) gets higher weight
        weights = np.array([1.5 if i == 0 else 1.0 for i in range(len(chunk_embeddings))], dtype=np.float32)
        weights /= np.sum(weights)
        pooled = np.sum(chunk_embeddings * weights[:, np.newaxis], axis=0)
        # Normalize L2
        norm = np.linalg.norm(pooled)
        if norm > 1e-6:
            pooled /= norm
        return pooled
