import json
import joblib
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging_config import logger


class LocalVectorStore:
    """
    Lightweight, high-performance CPU vector database with cosine similarity indexing.
    Persists locally to disk without requiring external servers.
    """
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (settings.DATA_PATH / "vector_index.joblib")
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None  # Shape: (N, D)
        self._is_loaded = False
        self.load()

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray) -> int:
        """Add new documents and their normalized dense vectors."""
        embeddings = np.array(embeddings, dtype=np.float32)
        # Ensure L2 normalization
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms

        if self.embeddings is None or len(self.documents) == 0:
            self.embeddings = embeddings
            self.documents = list(documents)
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            self.documents.extend(documents)

        self.save()
        logger.info(f"Added {len(documents)} documents to LocalVectorStore. Total: {len(self.documents)}")
        return len(self.documents)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Cosine similarity search over indexed evidence documents.
        """
        if self.embeddings is None or len(self.documents) == 0:
            return []

        query_vec = np.array(query_embedding, dtype=np.float32).flatten()
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        # Compute dot product (cosine similarity since both are L2 normalized)
        scores = np.dot(self.embeddings, query_vec)

        # Apply category filtering if specified
        if category and category.lower() != "all":
            valid_indices = [
                i for i, doc in enumerate(self.documents)
                if doc.get("category", "").lower() == category.lower()
            ]
            if not valid_indices:
                valid_indices = list(range(len(self.documents)))
        else:
            valid_indices = list(range(len(self.documents)))

        # Rank indices
        sub_scores = [(idx, scores[idx]) for idx in valid_indices]
        sub_scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in sub_scores[:top_k]:
            doc_copy = dict(self.documents[idx])
            doc_copy["similarity"] = round(float(score), 4)
            results.append(doc_copy)

        return results

    def save(self) -> None:
        """Persist vector index to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump({
                "documents": self.documents,
                "embeddings": self.embeddings
            }, self.storage_path)
        except Exception as e:
            logger.warning(f"Could not save vector store to disk: {e}")

    def load(self) -> bool:
        """Load persisted index from disk."""
        if self.storage_path.exists():
            try:
                data = joblib.load(self.storage_path)
                self.documents = data.get("documents", [])
                self.embeddings = data.get("embeddings", None)
                self._is_loaded = True
                logger.info(f"Loaded {len(self.documents)} documents from vector store at {self.storage_path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load vector store: {e}")
        return False

    def count(self) -> int:
        return len(self.documents)


vector_store = LocalVectorStore()
