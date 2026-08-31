from typing import Dict, Any, List
import numpy as np
from backend.app.evaluation.metrics import f1_score, accuracy_score
from backend.app.ml.baselines import TFIDFLogisticRegressionClassifier
from backend.app.core.logging_config import logger


class CrossDomainEvaluator:
    """
    Evaluates cross-domain generalization and domain transfer degradation.
    (e.g., Train on Politics, Test on Health or World News).
    """
    def evaluate_transfer(
        self,
        train_domain: str,
        test_domain: str,
        train_texts: List[str],
        train_labels: List[int],
        test_texts: List[str],
        test_labels: List[int]
    ) -> Dict[str, Any]:
        logger.info(f"Running Cross-Domain Evaluation: Train on '{train_domain}' ({len(train_texts)} samples) -> Test on '{test_domain}' ({len(test_texts)} samples)...")
        
        # 1. In-domain baseline: Split train set 80/20 to measure in-domain performance
        split_idx = int(len(train_texts) * 0.8)
        in_train_x, in_val_x = train_texts[:split_idx], train_texts[split_idx:]
        in_train_y, in_val_y = train_labels[:split_idx], train_labels[split_idx:]

        model = TFIDFLogisticRegressionClassifier(max_features=5000)
        model.train(in_train_x, in_train_y)
        
        in_domain_preds = model.predict(in_val_x)
        in_domain_f1 = float(f1_score(in_val_y, in_domain_preds, average="macro"))
        in_domain_acc = float(accuracy_score(in_val_y, in_domain_preds))

        # 2. Retrain on full train domain and test on target domain
        full_model = TFIDFLogisticRegressionClassifier(max_features=5000)
        full_model.train(train_texts, train_labels)

        cross_preds = full_model.predict(test_texts)
        cross_f1 = float(f1_score(test_labels, cross_preds, average="macro"))
        cross_acc = float(accuracy_score(test_labels, cross_preds))

        # 3. Degradation calculation
        degradation_f1 = round(max(0.0, (in_domain_f1 - cross_f1) / max(in_domain_f1, 0.001) * 100), 2)
        degradation_acc = round(max(0.0, (in_domain_acc - cross_acc) / max(in_domain_acc, 0.001) * 100), 2)

        return {
            "train_domain": train_domain,
            "test_domain": test_domain,
            "in_domain_macro_f1": round(in_domain_f1, 4),
            "in_domain_accuracy": round(in_domain_acc, 4),
            "cross_domain_macro_f1": round(cross_f1, 4),
            "cross_domain_accuracy": round(cross_acc, 4),
            "f1_performance_degradation_pct": degradation_f1,
            "accuracy_degradation_pct": degradation_acc,
            "transfer_robustness_rating": "High" if degradation_f1 < 10 else ("Moderate" if degradation_f1 < 25 else "Low")
        }


cross_domain_evaluator = CrossDomainEvaluator()
