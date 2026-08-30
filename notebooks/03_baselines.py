"""
Notebook 03: Baseline Model Benchmarking (TF-IDF + LR, TF-IDF + SVM, Passive-Aggressive)
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.core.config import settings
from backend.app.ml.baselines import TFIDFLogisticRegressionClassifier, TFIDFLinearSVMClassifier, PassiveAggressiveBaselineClassifier
from backend.app.evaluation.metrics import compute_comprehensive_metrics
from backend.app.services.dataset_service import dataset_service

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 03: Baseline Models Comparison")
    print("=" * 60)

    data_path = settings.BASE_PATH / "fake_news_data.csv"
    df = pd.read_csv(data_path, nrows=1000)
    df["label_int"] = dataset_service.normalize_labels(df["label"])
    
    texts = df["text"].fillna("").tolist()
    labels = df["label_int"].tolist()

    split = int(len(texts) * 0.8)
    train_x, test_x = texts[:split], texts[split:]
    train_y, test_y = labels[:split], labels[split:]

    for name, clf in [
        ("TFIDF + Logistic Regression", TFIDFLogisticRegressionClassifier(max_features=3000)),
        ("TFIDF + Linear SVM", TFIDFLinearSVMClassifier(max_features=3000)),
        ("Passive Aggressive", PassiveAggressiveBaselineClassifier(max_features=3000))
    ]:
        clf.train(train_x, train_y)
        preds = clf.predict(test_x).tolist()
        probs = clf.predict_proba(test_x)[:, 1].tolist()
        metrics = compute_comprehensive_metrics(test_y, preds, probs)
        print(f"\nModel: {name}")
        print(f"  Accuracy: {metrics['accuracy']:.4f} | Macro F1: {metrics['macro_f1']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f}")

if __name__ == "__main__":
    main()
