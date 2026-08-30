import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    roc_curve,
    confusion_matrix
)
from backend.app.ml.calibration import calculate_ece


def compute_comprehensive_metrics(y_true: List[int], y_pred: List[int], y_prob: List[float]) -> Dict[str, Any]:
    """
    Compute full research-grade evaluation metrics with calibration error,
    confusion matrix, and ROC/PR curve points.
    """
    y_t = np.array(y_true, dtype=np.int32)
    y_p = np.array(y_pred, dtype=np.int32)
    y_pr = np.array(y_prob, dtype=np.float64)

    acc = float(accuracy_score(y_t, y_p))
    prec_macro = float(precision_score(y_t, y_p, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_t, y_p, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_t, y_p, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_t, y_p, average="weighted", zero_division=0))

    # Binary specific
    prec_binary = float(precision_score(y_t, y_p, average="binary", zero_division=0))
    rec_binary = float(recall_score(y_t, y_p, average="binary", zero_division=0))
    f1_binary = float(f1_score(y_t, y_p, average="binary", zero_division=0))

    # Confusion matrix
    cm = confusion_matrix(y_t, y_p)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = int(cm[0, 0]), 0, 0, 0

    # ROC-AUC & PR-AUC
    try:
        roc_auc = float(roc_auc_score(y_t, y_pr))
    except Exception:
        roc_auc = 0.5

    # Curves for frontend charting (sampled to 10 points)
    try:
        fpr, tpr, _ = roc_curve(y_t, y_pr)
        step = max(1, len(fpr) // 10)
        roc_points = [{"fpr": round(float(fpr[i]), 3), "tpr": round(float(tpr[i]), 3)} for i in range(0, len(fpr), step)]
    except Exception:
        roc_points = [{"fpr": 0.0, "tpr": 0.0}, {"fpr": 1.0, "tpr": 1.0}]

    # Calibration error
    calib = calculate_ece(y_t, y_pr, n_bins=10)

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(f1_macro, 4),
        "weighted_f1": round(f1_weighted, 4),
        "macro_precision": round(prec_macro, 4),
        "macro_recall": round(rec_macro, 4),
        "binary_f1": round(f1_binary, 4),
        "binary_precision": round(prec_binary, 4),
        "binary_recall": round(rec_binary, 4),
        "roc_auc": round(roc_auc, 4),
        "expected_calibration_error": calib["ece"],
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "roc_curve": roc_points,
        "calibration_curve": calib["curve"]
    }
