import os
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Union, Optional
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    TfidfVectorizer = None
    TruncatedSVD = None
from backend.app.core.config import settings
from backend.app.core.resource_manager import resource_manager
from backend.app.core.logging_config import logger
from backend.app.ml.chunking import chunk_document, aggregate_chunk_embeddings


class BaseEmbeddingProvider(ABC):
    """Abstract base class for semantic text embeddings."""
    @abstractmethod
    def embed_text(self, text: str) -> np.ndarray:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """
    CPU-optimized sentence transformer using compact MiniLM (384 dimensions).
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dim = 384

    def _load(self):
        if self._model is None:
            logger.info(f"Loading SentenceTransformer model '{self.model_name}' on CPU...")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device="cpu")
                resource_manager.register_model(
                    f"embedding_{self.model_name}",
                    self._model,
                    {"type": "SentenceTransformer", "dim": 384, "device": "cpu"}
                )
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to CompactTFIDFEmbeddingProvider.")
                self._model = "FALLBACK"

    def embed_text(self, text: str) -> np.ndarray:
        self._load()
        if self._model == "FALLBACK" or self._model is None:
            fallback = CompactTFIDFEmbeddingProvider()
            return fallback.embed_text(text)

        # For long articles, chunk and aggregate
        chunks = chunk_document(text, max_tokens_per_chunk=settings.CHUNK_SIZE_TOKENS)
        if len(chunks) <= 1:
            vec = self._model.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0]
            return vec.astype(np.float32)

        chunk_texts = [c["text"] for c in chunks]
        chunk_vecs = self._model.encode(chunk_texts, convert_to_numpy=True, normalize_embeddings=True)
        return aggregate_chunk_embeddings(chunk_vecs)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        self._load()
        if self._model == "FALLBACK" or self._model is None:
            fallback = CompactTFIDFEmbeddingProvider()
            return fallback.embed_batch(texts)

        vecs = self._model.encode(texts, batch_size=16, convert_to_numpy=True, normalize_embeddings=True)
        return vecs.astype(np.float32)

    @property
    def dimension(self) -> int:
        return self._dim


class CompactTFIDFEmbeddingProvider(BaseEmbeddingProvider):
    """
    Ultra-lightweight, zero-download TF-IDF / Feature Hashing semantic projection provider.
    Guaranteed to run anywhere on CPU without any model downloads or heavy dependencies.
    """
    def __init__(self, n_components: int = 384):
        self._dim = n_components
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english") if HAS_SKLEARN else None
        self.svd = TruncatedSVD(n_components=min(n_components, 100), random_state=42) if HAS_SKLEARN else None
        self._is_fitted = False
        if HAS_SKLEARN:
            self._init_vocabulary()

    def _init_vocabulary(self):
        starter_corpus = [
            "government election politics vote senate congress president candidate",
            "health medical science vaccine disease virus hospital doctor treatment study",
            "technology artificial intelligence software internet cyber security algorithm computer",
            "breaking news report confirmed source official statement evidence facts investigation",
            "hoax fake news debunked conspiracy theory false claim fabricated misleading clickbait",
            "economy market financial inflation trade stock dollar bank employment growth",
            "international foreign relations diplomacy crisis military defense conflict alliance treaty",
            "climate environment weather crisis global warming temperature storm energy disaster"
        ] * 10
        X_tfidf = self.vectorizer.fit_transform(starter_corpus)
        n_comp = min(self._dim, X_tfidf.shape[1] - 1)
        self.svd = TruncatedSVD(n_components=n_comp, random_state=42)
        self.svd.fit(X_tfidf)
        self._is_fitted = True

    def embed_text(self, text: str) -> np.ndarray:
        if not text.strip():
            return np.zeros(self._dim, dtype=np.float32)
        if HAS_SKLEARN and self.vectorizer and self.svd:
            tfidf_vec = self.vectorizer.transform([text])
            dense_proj = self.svd.transform(tfidf_vec)[0]
            if len(dense_proj) < self._dim:
                padded = np.zeros(self._dim, dtype=np.float32)
                padded[:len(dense_proj)] = dense_proj
                dense_proj = padded
        else:
            # Fast numpy feature hashing fallback
            import re
            words = re.findall(r"\w+", text.lower())
            dense_proj = np.zeros(self._dim, dtype=np.float32)
            for word in words:
                idx = abs(hash(word)) % self._dim
                dense_proj[idx] += 1.0

        norm = np.linalg.norm(dense_proj)
        if norm > 1e-6:
            dense_proj /= norm
        return dense_proj.astype(np.float32)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return np.array([self.embed_text(t) for t in texts], dtype=np.float32)

    @property
    def dimension(self) -> int:
        return self._dim


_default_provider: Optional[BaseEmbeddingProvider] = None


def get_embedding_provider() -> BaseEmbeddingProvider:
    global _default_provider
    if _default_provider is None:
        try:
            _default_provider = SentenceTransformerEmbeddingProvider(settings.EMBEDDING_MODEL_NAME)
        except Exception as e:
            logger.warning(f"Defaulting to CompactTFIDFEmbeddingProvider due to: {e}")
            _default_provider = CompactTFIDFEmbeddingProvider()
    return _default_provider
