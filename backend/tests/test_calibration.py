import pytest
import numpy as np
from backend.app.ml.calibration import ConfidenceCalibrator, calculate_ece


def test_confidence_calibration():
    calibrator = ConfidenceCalibrator(method="platt")
    raw_probs = np.array([0.1, 0.2, 0.8, 0.9, 0.15, 0.85])
    y_true = np.array([0, 0, 1, 1, 0, 1])

    calibrator.fit(raw_probs, y_true)
    assert calibrator.is_fitted

    calib_val = calibrator.calibrate(0.95)
    assert 0.0 < calib_val < 1.0


def test_calculate_ece():
    y_true = np.array([0, 0, 0, 1, 1, 1, 1, 1, 0, 1])
    y_prob = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.85, 0.9, 0.95, 0.4, 0.6])

    metrics = calculate_ece(y_true, y_prob, n_bins=5)
    assert "ece" in metrics
    assert "mce" in metrics
    assert 0.0 <= metrics["ece"] <= 1.0
    assert len(metrics["curve"]) == 5
