"""
Notebook 09: Cross-Domain Transfer & Domain Shift Degradation
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.core.config import settings
from backend.app.evaluation.cross_domain import cross_domain_evaluator
from backend.app.services.dataset_service import dataset_service

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 09: Cross-Domain Generalization")
    print("=" * 60)

    data_path = settings.BASE_PATH / "fake_news_data.csv"
    if not data_path.exists():
        print(f"Data file not found at {data_path}")
        return

    df = pd.read_csv(data_path, nrows=2000)
    df["label_int"] = dataset_service.normalize_labels(df["label"])

    pol_df = df[df["subject"].str.lower().str.contains("politics")].head(200)
    world_df = df[df["subject"].str.lower().str.contains("world")].head(200)

    if len(pol_df) >= 50 and len(world_df) >= 50:
        res = cross_domain_evaluator.evaluate_transfer(
            train_domain="Politics",
            test_domain="World News",
            train_texts=pol_df["text"].fillna("").tolist(),
            train_labels=pol_df["label_int"].tolist(),
            test_texts=world_df["text"].fillna("").tolist(),
            test_labels=world_df["label_int"].tolist()
        )
        print(f"In-Domain F1 (Politics -> Politics): {res['in_domain_macro_f1']:.4f}")
        print(f"Cross-Domain F1 (Politics -> World News): {res['cross_domain_macro_f1']:.4f}")
        print(f"F1 Degradation: {res['f1_performance_degradation_pct']}%")
        print(f"Transfer Robustness Rating: {res['transfer_robustness_rating']}")

if __name__ == "__main__":
    main()
