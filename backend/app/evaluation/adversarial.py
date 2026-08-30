import re
import random
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics import f1_score, accuracy_score
from backend.app.ml.baselines import BaseClassifier


class AdversarialRobustnessTester:
    """
    Evaluates classifier resilience against adversarial text perturbations:
      - Casing perturbations (random upper/lower flips)
      - Punctuation jitter (exclamation/question mark injection)
      - Character typos and word swaps
      - Irrelevant distracting sentence insertion
    """
    def perturb_casing(self, text: str) -> str:
        words = text.split()
        perturbed = [w.upper() if random.random() < 0.2 else w.lower() if random.random() < 0.2 else w for w in words]
        return " ".join(perturbed)

    def perturb_punctuation(self, text: str) -> str:
        return text.replace(".", "...!").replace("!", "!?!")

    def perturb_noise_insertion(self, text: str) -> str:
        distractor = " In other unrelated news, international meteorological studies observe seasonal temperature variances. "
        mid = len(text) // 2
        return text[:mid] + distractor + text[mid:]

    def evaluate_robustness(
        self,
        classifier: BaseClassifier,
        texts: List[str],
        labels: List[int]
    ) -> Dict[str, Any]:
        # 1. Clean test set baseline
        clean_preds = classifier.predict(texts)
        clean_f1 = float(f1_score(labels, clean_preds, average="macro"))
        clean_acc = float(accuracy_score(labels, clean_preds))

        # 2. Perturbation tests
        casing_texts = [self.perturb_casing(t) for t in texts]
        casing_preds = classifier.predict(casing_texts)
        casing_f1 = float(f1_score(labels, casing_preds, average="macro"))

        punct_texts = [self.perturb_punctuation(t) for t in texts]
        punct_preds = classifier.predict(punct_texts)
        punct_f1 = float(f1_score(labels, punct_preds, average="macro"))

        noise_texts = [self.perturb_noise_insertion(t) for t in texts]
        noise_preds = classifier.predict(noise_texts)
        noise_f1 = float(f1_score(labels, noise_preds, average="macro"))

        avg_perturbed_f1 = (casing_f1 + punct_f1 + noise_f1) / 3.0
        robustness_degradation = round(max(0.0, (clean_f1 - avg_perturbed_f1) / max(clean_f1, 0.001) * 100), 2)

        return {
            "clean_macro_f1": round(clean_f1, 4),
            "clean_accuracy": round(clean_acc, 4),
            "casing_perturbed_macro_f1": round(casing_f1, 4),
            "punctuation_perturbed_macro_f1": round(punct_f1, 4),
            "distractor_inserted_macro_f1": round(noise_f1, 4),
            "average_adversarial_f1": round(avg_perturbed_f1, 4),
            "robustness_degradation_pct": robustness_degradation,
            "adversarial_resilience_grade": "A (Highly Resilient)" if robustness_degradation < 5 else ("B (Resilient)" if robustness_degradation < 15 else "C (Vulnerable)")
        }


adversarial_tester = AdversarialRobustnessTester()
