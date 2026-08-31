try:
    import joblib
except ImportError:
    joblib = None
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import re
from collections import Counter
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

    class PurePythonVectorizer:
        def __init__(self, max_features: int = 1000, ngram_range=(1, 2), stop_words="english", sublinear_tf=True):
            self.max_features = max_features
            self.vocab = {}
            self.idf = {}
            self.vocabulary_ = {}

        def _tokenize(self, text: str) -> List[str]:
            words = re.findall(r"\b[a-zA-Z]{2,}\b", str(text).lower())
            # Unigrams + bigrams
            unigrams = [w for w in words if w not in {"the", "a", "an", "and", "or", "in", "of", "to", "is", "for", "on", "that", "this", "with", "as", "by", "at"}]
            bigrams = [f"{unigrams[i]}_{unigrams[i+1]}" for i in range(len(unigrams)-1)]
            return unigrams + bigrams

        def fit_transform(self, texts: List[str]) -> np.ndarray:
            doc_tokens = [self._tokenize(t) for t in texts]
            df = Counter()
            for toks in doc_tokens:
                for w in set(toks):
                    df[w] += 1
            top_words = [w for w, _ in df.most_common(self.max_features)]
            self.vocab = {w: i for i, w in enumerate(top_words)}
            self.vocabulary_ = dict(self.vocab)
            n_docs = len(texts)
            self.idf = {w: np.log((1 + n_docs) / (1 + df[w])) + 1.0 for w in self.vocab}
            return self.transform(texts)

        def transform(self, texts: List[str]) -> np.ndarray:
            X = np.zeros((len(texts), max(1, len(self.vocab))), dtype=np.float32)
            if not self.vocab:
                return X
            for i, text in enumerate(texts):
                toks = self._tokenize(text)
                counts = Counter(toks)
                for w, c in counts.items():
                    if w in self.vocab:
                        j = self.vocab[w]
                        tf = 1.0 + np.log(c) if c > 0 else 0.0
                        X[i, j] = tf * self.idf.get(w, 1.0)
                norm = np.linalg.norm(X[i])
                if norm > 0:
                    X[i] /= norm
            return X

        def get_feature_names_out(self) -> List[str]:
            inv = sorted(self.vocab.items(), key=lambda x: x[1])
            return [w for w, _ in inv]

    class PurePythonLogisticRegression:
        def __init__(self, C: float = 1.0, max_iter: int = 200, solver="lbfgs", random_state=42):
            self.C = C
            self.max_iter = max_iter
            self.weights = None
            self.bias = 0.0
            self.coef_ = np.array([[]])

        def fit(self, X: np.ndarray, y: np.ndarray):
            n_samples, n_features = X.shape
            self.weights = np.zeros(n_features, dtype=np.float64)
            self.bias = 0.0
            y_arr = np.array(y, dtype=np.float64)
            lr = 0.1
            for _ in range(min(self.max_iter, 100)):
                linear = np.dot(X, self.weights) + self.bias
                probs = 1.0 / (1.0 + np.exp(-np.clip(linear, -15, 15)))
                dw = (1.0 / max(1, n_samples)) * np.dot(X.T, (probs - y_arr)) + (0.01 * self.weights)
                db = (1.0 / max(1, n_samples)) * np.sum(probs - y_arr)
                self.weights -= lr * dw
                self.bias -= lr * db
            self.coef_ = np.array([self.weights])

        def predict_proba(self, X: np.ndarray) -> np.ndarray:
            if self.weights is None:
                p = np.full((len(X), 2), 0.5)
                return p
            linear = np.dot(X, self.weights) + self.bias
            p1 = 1.0 / (1.0 + np.exp(-np.clip(linear, -15, 15)))
            p0 = 1.0 - p1
            return np.column_stack([p0, p1])

        def predict(self, X: np.ndarray) -> np.ndarray:
            return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

    class PurePythonCalibratedModel:
        def __init__(self, base_estimator, cv=3):
            self.base_estimator = base_estimator
            self.calibrated_classifiers_ = []

        def fit(self, X: np.ndarray, y: np.ndarray):
            self.base_estimator.fit(X, y)
            class MockClf:
                def __init__(self, est):
                    self.estimator = est
            self.calibrated_classifiers_ = [MockClf(self.base_estimator)]

        def predict_proba(self, X: np.ndarray) -> np.ndarray:
            return self.base_estimator.predict_proba(X)

        def predict(self, X: np.ndarray) -> np.ndarray:
            return self.base_estimator.predict(X)

    TfidfVectorizer = PurePythonVectorizer
    LogisticRegression = PurePythonLogisticRegression
    PassiveAggressiveClassifier = PurePythonLogisticRegression
    LinearSVC = PurePythonLogisticRegression
    CalibratedClassifierCV = PurePythonCalibratedModel
from backend.app.core.logging_config import logger


class BaseClassifier:
    """Abstract interface for all VeritasAI classification models."""
    def train(self, texts: List[str], labels: List[int], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def predict(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def explain(self, text: str, top_k: int = 10) -> Dict[str, Any]:
        raise NotImplementedError

    def save(self, filepath: Path) -> None:
        raise NotImplementedError

    def load(self, filepath: Path) -> None:
        raise NotImplementedError


class TFIDFLogisticRegressionClassifier(BaseClassifier):
    """
    Baseline 1: TF-IDF (unigrams + bigrams) + L2 Regularized Logistic Regression.
    """
    def __init__(self, max_features: int = 10000, C: float = 1.0):
        self.max_features = max_features
        self.C = C
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        self.model = LogisticRegression(C=C, max_iter=500, solver="lbfgs", random_state=42)
        self.is_fitted = False

    def train(self, texts: List[str], labels: List[int], **kwargs) -> Dict[str, Any]:
        logger.info(f"Training TF-IDF + Logistic Regression on {len(texts)} samples...")
        X = self.vectorizer.fit_transform(texts)
        y = np.array(labels)
        self.model.fit(X, y)
        self.is_fitted = True
        return {"status": "trained", "samples": len(texts), "vocab_size": len(self.vectorizer.vocabulary_)}

    def predict(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not trained yet.")
        X = self.vectorizer.transform(texts)
        return self.model.predict(X)

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not trained yet.")
        X = self.vectorizer.transform(texts)
        return self.model.predict_proba(X)

    def explain(self, text: str, top_k: int = 10) -> Dict[str, Any]:
        if not self.is_fitted:
            return {"top_features": []}
        X = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        nonzero_indices = X.nonzero()[1]
        
        coefficients = self.model.coef_[0]
        word_scores = []
        for idx in nonzero_indices:
            word = feature_names[idx]
            tfidf_val = X[0, idx]
            weight = coefficients[idx]
            contribution = tfidf_val * weight  # positive = Fake (if label 1 is Fake), negative = Real
            word_scores.append({
                "token": word,
                "score": float(round(contribution, 4)),
                "weight": float(round(weight, 4)),
                "tfidf": float(round(tfidf_val, 4))
            })

        word_scores.sort(key=lambda x: abs(x["score"]), reverse=True)
        return {"top_features": word_scores[:top_k]}

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"vectorizer": self.vectorizer, "model": self.model, "is_fitted": self.is_fitted}, filepath)

    def load(self, filepath: Path) -> None:
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.model = data["model"]
        self.is_fitted = data.get("is_fitted", True)


class TFIDFLinearSVMClassifier(BaseClassifier):
    """
    Baseline 2: TF-IDF + Linear Support Vector Machine with probability calibration.
    """
    def __init__(self, max_features: int = 10000, C: float = 1.0):
        self.max_features = max_features
        self.C = C
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        self.svm = LinearSVC(C=C, max_iter=1000, random_state=42)
        self.calibrated_model: Optional[CalibratedClassifierCV] = None
        self.is_fitted = False

    def train(self, texts: List[str], labels: List[int], **kwargs) -> Dict[str, Any]:
        logger.info(f"Training TF-IDF + Linear SVM on {len(texts)} samples...")
        X = self.vectorizer.fit_transform(texts)
        y = np.array(labels)
        self.calibrated_model = CalibratedClassifierCV(self.svm, cv=3)
        self.calibrated_model.fit(X, y)
        self.is_fitted = True
        return {"status": "trained", "samples": len(texts), "vocab_size": len(self.vectorizer.vocabulary_)}

    def predict(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted or self.calibrated_model is None:
            raise ValueError("Model is not trained yet.")
        X = self.vectorizer.transform(texts)
        return self.calibrated_model.predict(X)

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted or self.calibrated_model is None:
            raise ValueError("Model is not trained yet.")
        X = self.vectorizer.transform(texts)
        return self.calibrated_model.predict_proba(X)

    def explain(self, text: str, top_k: int = 10) -> Dict[str, Any]:
        # Feature weights from the underlying calibrated estimators
        if not self.is_fitted or not self.calibrated_model:
            return {"top_features": []}
        X = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        nonzero_indices = X.nonzero()[1]

        # Average weights across CV folds
        weights = np.mean([clf.estimator.coef_[0] for clf in self.calibrated_model.calibrated_classifiers_], axis=0)
        word_scores = []
        for idx in nonzero_indices:
            word = feature_names[idx]
            tfidf_val = X[0, idx]
            weight = weights[idx]
            contribution = tfidf_val * weight
            word_scores.append({
                "token": word,
                "score": float(round(contribution, 4)),
                "weight": float(round(weight, 4)),
                "tfidf": float(round(tfidf_val, 4))
            })

        word_scores.sort(key=lambda x: abs(x["score"]), reverse=True)
        return {"top_features": word_scores[:top_k]}

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"vectorizer": self.vectorizer, "calibrated_model": self.calibrated_model, "is_fitted": self.is_fitted}, filepath)

    def load(self, filepath: Path) -> None:
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.calibrated_model = data["calibrated_model"]
        self.is_fitted = data.get("is_fitted", True)


class PassiveAggressiveBaselineClassifier(BaseClassifier):
    """
    Baseline 3: Passive Aggressive Classifier with Sigmoid Probability Calibration.
    """
    def __init__(self, max_features: int = 10000, max_iter: int = 100):
        self.max_features = max_features
        self.max_iter = max_iter
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
        self.pac = PassiveAggressiveClassifier(max_iter=max_iter, random_state=42)
        self.calibrated_model: Optional[CalibratedClassifierCV] = None
        self.is_fitted = False

    def train(self, texts: List[str], labels: List[int], **kwargs) -> Dict[str, Any]:
        X = self.vectorizer.fit_transform(texts)
        y = np.array(labels)
        self.calibrated_model = CalibratedClassifierCV(self.pac, cv=3)
        self.calibrated_model.fit(X, y)
        self.is_fitted = True
        return {"status": "trained", "samples": len(texts)}

    def predict(self, texts: List[str]) -> np.ndarray:
        X = self.vectorizer.transform(texts)
        return self.calibrated_model.predict(X)

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        X = self.vectorizer.transform(texts)
        return self.calibrated_model.predict_proba(X)

    def explain(self, text: str, top_k: int = 10) -> Dict[str, Any]:
        if not self.is_fitted or not self.calibrated_model:
            return {"top_features": []}
        X = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        nonzero_indices = X.nonzero()[1]
        weights = np.mean([clf.estimator.coef_[0] for clf in self.calibrated_model.calibrated_classifiers_], axis=0)
        word_scores = []
        for idx in nonzero_indices:
            word = feature_names[idx]
            tfidf_val = X[0, idx]
            weight = weights[idx]
            contribution = tfidf_val * weight
            word_scores.append({
                "token": word,
                "score": float(round(contribution, 4)),
                "weight": float(round(weight, 4))
            })
        word_scores.sort(key=lambda x: abs(x["score"]), reverse=True)
        return {"top_features": word_scores[:top_k]}

    def save(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"vectorizer": self.vectorizer, "calibrated_model": self.calibrated_model, "is_fitted": self.is_fitted}, filepath)

    def load(self, filepath: Path) -> None:
        data = joblib.load(filepath)
        self.vectorizer = data["vectorizer"]
        self.calibrated_model = data["calibrated_model"]
        self.is_fitted = data.get("is_fitted", True)
