import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.ml.model_registry import model_registry
from backend.app.ml.embeddings import get_embedding_provider
from backend.app.ml.preprocessing import extract_linguistic_signals
from backend.app.evaluation.metrics import compute_comprehensive_metrics
from backend.app.services.dataset_service import dataset_service


def train_all_models(sample_limit: int = 1500):
    """
    Train and save all baseline models (TFIDF_LogisticRegression, TFIDF_LinearSVM,
    PassiveAggressive) and the VeritasFusion multimodal engine.
    """
    data_path = settings.BASE_PATH / "fake_news_data.csv"
    if not data_path.exists():
        logger.error(f"Dataset {data_path} not found!")
        return

    logger.info(f"Loading {data_path.name} (subsampling {sample_limit} for CPU training)...")
    df = pd.read_csv(data_path, low_memory=False)
    sub_df = df.sample(n=min(sample_limit, len(df)), random_state=42).reset_index(drop=True)
    
    sub_df["label_int"] = dataset_service.normalize_labels(sub_df["label"])
    texts = sub_df["text"].fillna("").astype(str).tolist()
    labels = sub_df["label_int"].tolist()

    split_idx = int(len(texts) * 0.8)
    train_texts, test_texts = texts[:split_idx], texts[split_idx:]
    train_labels, test_labels = labels[:split_idx], labels[split_idx:]

    logger.info(f"Train samples: {len(train_texts)}, Test samples: {len(test_texts)}")

    # 1. Train Classical Baselines
    for model_name in ["TFIDF_LogisticRegression", "TFIDF_LinearSVM", "PassiveAggressive"]:
        logger.info(f"--- Training {model_name} ---")
        start = time.time()
        model = model_registry.models[model_name]
        model.train(train_texts, train_labels)
        
        preds = model.predict(test_texts).tolist()
        probs = model.predict_proba(test_texts)[:, 1].tolist()
        
        elapsed = round(time.time() - start, 2)
        metrics = compute_comprehensive_metrics(test_labels, preds, probs)
        metrics["training_time_seconds"] = elapsed
        
        model_registry.save_checkpoint(model_name)
        model_registry.update_metrics(model_name, metrics)
        logger.info(f"✅ {model_name} trained in {elapsed}s -> Accuracy: {metrics['accuracy']}, Macro F1: {metrics['macro_f1']}")

    # 2. Train VeritasFusion Multimodal Engine
    logger.info("--- Training VeritasFusion Multimodal Engine ---")
    start = time.time()
    embedder = get_embedding_provider()
    
    logger.info("Computing dense text embeddings for VeritasFusion...")
    train_embs = embedder.embed_batch(train_texts)
    test_embs = embedder.embed_batch(test_texts)

    train_ling = [extract_linguistic_signals(t) for t in train_texts]
    test_ling = [extract_linguistic_signals(t) for t in test_texts]

    vf_model = model_registry.models["VeritasFusion"]
    vf_model.train(train_embs, train_ling, train_labels)

    preds = []
    probs = []
    for i in range(len(test_texts)):
        res = vf_model.predict_multimodal(test_embs[i], test_ling[i])
        preds.append(1 if res["verdict"] == "LIKELY_FAKE" else 0)
        probs.append(res["raw_fake_probability"])

    elapsed = round(time.time() - start, 2)
    metrics = compute_comprehensive_metrics(test_labels, preds, probs)
    metrics["training_time_seconds"] = elapsed

    model_registry.save_checkpoint("VeritasFusion")
    model_registry.update_metrics("VeritasFusion", metrics)
    logger.info(f"✅ VeritasFusion trained in {elapsed}s -> Accuracy: {metrics['accuracy']}, Macro F1: {metrics['macro_f1']}")
    logger.info("🎉 All starter models trained and saved to models/checkpoints/!")


if __name__ == "__main__":
    train_all_models(sample_limit=1200)
