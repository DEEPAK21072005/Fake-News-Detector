import numpy as np
from typing import Dict, Any, Tuple, List, Optional
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.isotonic import IsotonicRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    from backend.app.ml.baselines import LogisticRegression
    IsotonicRegression = None


class ConfidenceCalibrator:
    """
    Confidence calibration module implementing Platt Scaling, Isotonic Regression,
    and Expected Calibration Error (ECE) measurement.
    """
    def __init__(self, method: str = "platt"):
        self.method = method  # "platt" | "isotonic" | "temperature"
        self.platt_model: Optional[LogisticRegression] = None
        self.isotonic_model: Optional[IsotonicRegression] = None
        self.temperature: float = 1.0
        self.is_fitted: bool = False

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray):
        """Fit calibration mapping on validation set."""
        raw_probs = np.clip(np.array(raw_probs, dtype=np.float64), 1e-6, 1.0 - 1e-6)
        y_true = np.array(y_true, dtype=np.int32)

        if self.method == "platt":
            logits = np.log(raw_probs / (1.0 - raw_probs)).reshape(-1, 1)
            self.platt_model = LogisticRegression(C=1.0, solver="lbfgs")
            self.platt_model.fit(logits, y_true)
        elif self.method == "isotonic":
            self.isotonic_model = IsotonicRegression(out_of_bounds="clip")
            self.isotonic_model.fit(raw_probs, y_true)
        elif self.method == "temperature":
            # Simple grid search for temperature T minimizing NLL
            best_t, best_loss = 1.0, float("inf")
            logits = np.log(raw_probs / (1.0 - raw_probs))
            for t in np.linspace(0.5, 3.0, 50):
                scaled_probs = 1.0 / (1.0 + np.exp(-logits / t))
                nll = -np.mean(y_true * np.log(np.clip(scaled_probs, 1e-6, 1.0)) + 
                               (1 - y_true) * np.log(np.clip(1.0 - scaled_probs, 1e-6, 1.0)))
                if nll < best_loss:
                    best_loss, best_t = nll, t
            self.temperature = best_t

        self.is_fitted = True

    def calibrate(self, raw_prob: float) -> float:
        """Calibrate a single probability score."""
        raw_prob = float(np.clip(raw_prob, 1e-6, 1.0 - 1e-6))
        if not self.is_fitted:
            # Heuristic default soft calibration
            # Squeezes overconfident probabilities closer to uninformative prior
            logit = np.log(raw_prob / (1.0 - raw_prob))
            calibrated = 1.0 / (1.0 + np.exp(-logit / 1.35))
            return float(np.clip(calibrated, 0.05, 0.95))

        if self.method == "platt" and self.platt_model is not None:
            logit = np.log(raw_prob / (1.0 - raw_prob)).reshape(-1, 1)
            calibrated = self.platt_model.predict_proba(logit)[0, 1]
        elif self.method == "isotonic" and self.isotonic_model is not None:
            calibrated = self.isotonic_model.predict([raw_prob])[0]
        elif self.method == "temperature":
            logit = np.log(raw_prob / (1.0 - raw_prob))
            calibrated = 1.0 / (1.0 + np.exp(-logit / self.temperature))
        else:
            calibrated = raw_prob

        return float(np.clip(calibrated, 0.01, 0.99))


def calculate_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> Dict[str, Any]:
    """
    Calculate Expected Calibration Error (ECE), Maximum Calibration Error (MCE),
    and bin-level accuracy vs confidence data for calibration curves.
    """
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    mce = 0.0
    curve_data = []

    for i in range(n_bins):
        bin_lower, bin_upper = bin_edges[i], bin_edges[i + 1]
        mask = (y_prob >= bin_lower) & (y_prob < bin_upper) if i < n_bins - 1 else (y_prob >= bin_lower) & (y_prob <= bin_upper)
        
        bin_count = int(np.sum(mask))
        if bin_count > 0:
            bin_acc = float(np.mean(y_true[mask]))
            bin_conf = float(np.mean(y_prob[mask]))
            gap = abs(bin_acc - bin_conf)
            ece += (bin_count / len(y_true)) * gap
            mce = max(mce, gap)

            curve_data.append({
                "bin": f"{bin_lower:.1f}-{bin_upper:.1f}",
                "confidence": round(bin_conf, 3),
                "accuracy": round(bin_acc, 3),
                "count": bin_count,
                "gap": round(gap, 3)
            })
        else:
            curve_data.append({
                "bin": f"{bin_lower:.1f}-{bin_upper:.1f}",
                "confidence": round((bin_lower + bin_upper) / 2.0, 3),
                "accuracy": 0.0,
                "count": 0,
                "gap": 0.0
            })

    return {
        "ece": round(float(ece), 4),
        "mce": round(float(mce), 4),
        "curve": curve_data
    }
