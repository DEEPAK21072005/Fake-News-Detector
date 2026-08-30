try:
    import joblib
except ImportError:
    joblib = None
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression, PassiveAggressiveClassifier
    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    TfidfVectorizer = None
    LogisticRegression = None
    PassiveAggressiveClassifier = None
    LinearSVC = None
    CalibratedClassifierCV = None
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
        ) if HAS_SKLEARN else None
        self.model = LogisticRegression(C=C, max_iter=500, solver="lbfgs", random_state=42) if HAS_SKLEARN else None
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
        ) if HAS_SKLEARN else None
        self.svm = LinearSVC(C=C, max_iter=1000, random_state=42) if HAS_SKLEARN else None
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
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english") if HAS_SKLEARN else None
        self.pac = PassiveAggressiveClassifier(max_iter=max_iter, random_state=42) if HAS_SKLEARN else None
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
