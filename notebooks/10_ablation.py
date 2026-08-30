"""
Notebook 10: Multi-Component Empirical Ablation Studies
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.core.config import settings
from backend.app.evaluation.ablation import ablation_runner
from backend.app.services.dataset_service import dataset_service

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 10: Component Ablation Suite")
    print("=" * 60)

    data_path = settings.BASE_PATH / "fake_news_data.csv"
    if not data_path.exists():
        print(f"Data file not found at {data_path}")
        return

    df = pd.read_csv(data_path, nrows=400)
    df["label_int"] = dataset_service.normalize_labels(df["label"])

    texts = df["text"].fillna("").tolist()
    labels = df["label_int"].tolist()

    results = ablation_runner.run_ablation_suite(texts, labels, sample_limit=250)

    print("\n" + "=" * 75)
    print(f"{'Configuration':<45} | {'Macro F1':<10} | {'Accuracy':<10}")
    print("-" * 75)
    for r in results:
        print(f"{r['configuration']:<45} | {r['macro_f1']:<10.4f} | {r['accuracy']:<10.4f}")
    print("=" * 75)

if __name__ == "__main__":
    main()
