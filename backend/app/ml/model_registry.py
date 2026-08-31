import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.core.resource_manager import resource_manager
from backend.app.ml.baselines import (
    BaseClassifier,
    TFIDFLogisticRegressionClassifier,
    TFIDFLinearSVMClassifier,
    PassiveAggressiveBaselineClassifier
)
from backend.app.ml.veritas_fusion import VeritasFusionEngine


class ModelRegistry:
    """
    Central model registry and lifecycle manager for all VeritasAI models.
    """
    _instance: Optional["ModelRegistry"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.models: Dict[str, Any] = {}
        self.model_cards: Dict[str, Dict[str, Any]] = {}
        self.active_model_name: str = "VeritasFusion"
        self._init_defaults()

    def _init_defaults(self):
        """Instantiate default model instances."""
        self.models["TFIDF_LogisticRegression"] = TFIDFLogisticRegressionClassifier()
        self.models["TFIDF_LinearSVM"] = TFIDFLinearSVMClassifier()
        self.models["PassiveAggressive"] = PassiveAggressiveBaselineClassifier()
        self.models["VeritasFusion"] = VeritasFusionEngine()

        # Initialize base model cards
        for name, arch, desc in [
            ("TFIDF_LogisticRegression", "TF-IDF (1-2 n-grams) + Logistic Regression", "Linear statistical baseline model."),
            ("TFIDF_LinearSVM", "TF-IDF + Calibrated Linear SVM", "Support Vector Machine baseline with probability calibration."),
            ("PassiveAggressive", "TF-IDF + Calibrated Passive-Aggressive", "Online learning passive-aggressive classifier."),
            ("VeritasFusion", "Multimodal Fusion (MiniLM + Stylometry + Evidence + Stance)", "Flagship multimodal verification architecture.")
        ]:
            self.model_cards[name] = {
                "model_name": name,
                "architecture": arch,
                "description": desc,
                "dataset": "ISOT Fake News Corpus",
                "training_status": "Ready / Initialized",
                "created_at": datetime.datetime.utcnow().isoformat(),
                "metrics": {
                    "accuracy": None,
                    "macro_f1": None,
                    "weighted_f1": None,
                    "roc_auc": None,
                    "status": "Not evaluated yet"
                },
                "intended_use": "AI-assisted fake news pattern detection and multimodal evidence verification.",
                "limitations": "Model assesses stylistic cues and evidence retrieval. It is not an absolute arbiter of truth."
            }

        logger.info(f"ModelRegistry initialized with {len(self.models)} architectures.")

    def get_active_model(self) -> Any:
        return self.models.get(self.active_model_name, self.models["VeritasFusion"])

    def set_active_model(self, name: str) -> str:
        if name in self.models:
            self.active_model_name = name
            logger.info(f"Active model set to: {name}")
            return name
        raise ValueError(f"Model '{name}' not found. Available: {list(self.models.keys())}")

    def get_model_card(self, name: str) -> Dict[str, Any]:
        return self.model_cards.get(name, {
            "model_name": name,
            "error": "Model card not found."
        })

    def update_metrics(self, name: str, metrics: Dict[str, Any]) -> None:
        if name in self.model_cards:
            self.model_cards[name]["metrics"] = metrics
            self.model_cards[name]["training_status"] = "Trained & Evaluated"
            self.model_cards[name]["updated_at"] = datetime.datetime.utcnow().isoformat()

    def list_models(self) -> List[Dict[str, Any]]:
        results = []
        for name, instance in self.models.items():
            card = self.model_cards.get(name, {})
            is_fitted = getattr(instance, "is_fitted", False)
            results.append({
                "name": name,
                "architecture": card.get("architecture", name),
                "is_active": (name == self.active_model_name),
                "is_trained": is_fitted,
                "metrics": card.get("metrics", {}),
                "intended_use": card.get("intended_use", "")
            })
        return results

    def save_checkpoint(self, name: str, filepath: Optional[Path] = None) -> Optional[Path]:
        if name not in self.models:
            raise ValueError(f"Model {name} not found.")
        if filepath is None:
            filepath = settings.CHECKPOINTS_PATH / f"{name.lower()}_checkpoint.joblib"
        try:
            self.models[name].save(filepath)
            logger.info(f"Saved checkpoint for {name} to {filepath}")
            return filepath
        except Exception as e:
            logger.warning(f"Could not persist checkpoint for {name}: {e}")
            return None

    def load_checkpoint(self, name: str, filepath: Path) -> None:
        if name not in self.models:
            raise ValueError(f"Model {name} not found.")
        if filepath.exists():
            self.models[name].load(filepath)
            if name in self.model_cards:
                self.model_cards[name]["training_status"] = "Loaded from checkpoint"
            logger.info(f"Loaded checkpoint for {name} from {filepath}")


model_registry = ModelRegistry()
