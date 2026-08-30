"""
Notebook 08: Comprehensive Metric Evaluation (Accuracy, Macro F1, ECE Calibration Error, ROC/PR)
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.evaluation.metrics import compute_comprehensive_metrics

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 08: Evaluation Metrics & Calibration")
    print("=" * 60)

    y_true = [0, 0, 1, 1, 0, 1, 0, 1, 1, 0]
    y_pred = [0, 0, 1, 1, 0, 1, 1, 1, 0, 0]
    y_prob = [0.12, 0.25, 0.88, 0.92, 0.15, 0.79, 0.62, 0.85, 0.40, 0.18]

    metrics = compute_comprehensive_metrics(y_true, y_pred, y_prob)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1: {metrics['macro_f1']:.4f}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"Expected Calibration Error (ECE): {metrics['expected_calibration_error']:.4f}")
    print(f"Confusion Matrix: {metrics['confusion_matrix']}")

if __name__ == "__main__":
    main()
