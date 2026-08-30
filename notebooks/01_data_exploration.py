"""
Notebook 01: Exploratory Data Analysis & Class Balance Analysis
Analyzes dataset distribution, text length statistics, vocabulary frequency, and domain representation.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.core.config import settings

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 01: Exploratory Data Analysis")
    print("=" * 60)

    data_path = settings.BASE_PATH / "fake_news_data.csv"
    if not data_path.exists():
        print(f"Data file not found at {data_path}")
        return

    df = pd.read_csv(data_path, nrows=5000)
    print(f"Loaded {len(df)} sample rows from {data_path.name}")
    print(f"Columns: {df.columns.tolist()}")

    print("\nClass Distribution:")
    print(df["label"].value_counts())

    if "subject" in df.columns:
        print("\nSubject / Domain Distribution:")
        print(df["subject"].value_counts())

    df["word_count"] = df["text"].fillna("").apply(lambda t: len(str(t).split()))
    print("\nArticle Word Count Statistics:")
    print(df["word_count"].describe())

if __name__ == "__main__":
    main()
