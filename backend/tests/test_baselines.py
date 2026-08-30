import pytest
import numpy as np
from backend.app.ml.baselines import (
    TFIDFLogisticRegressionClassifier,
    TFIDFLinearSVMClassifier,
    PassiveAggressiveBaselineClassifier
)


def test_baseline_classifiers_lifecycle():
    texts = [
        "Government passes federal budget for public transportation infrastructure.",
        "Official election results certified by state board of elections.",
        "SHOCKING SECRET: Miracle cure destroys all illnesses overnight secretly!",
        "BOMBSHELL: Alien conspiracy covered up by deep state elites!"
    ] * 5
    labels = [0, 0, 1, 1] * 5

    for ClfClass in [TFIDFLogisticRegressionClassifier, TFIDFLinearSVMClassifier, PassiveAggressiveBaselineClassifier]:
        clf = ClfClass(max_features=500)
        res = clf.train(texts, labels)
        assert res["status"] == "trained"

        test_real = ["Official municipal government council meeting summary."]
        test_fake = ["UNBELIEVABLE BOMBSHELL SECRET EXPOSED!"]

        pred_real = clf.predict(test_real)
        pred_fake = clf.predict(test_fake)
        assert len(pred_real) == 1
        assert len(pred_fake) == 1

        probs = clf.predict_proba(test_real)
        assert probs.shape == (1, 2)
        assert 0.0 <= probs[0, 0] <= 1.0

        expl = clf.explain(test_fake[0])
        assert "top_features" in expl
