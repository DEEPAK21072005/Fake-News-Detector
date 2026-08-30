import time
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import numpy as np

from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.database.database import get_db
from backend.app.ml.model_registry import model_registry
from backend.app.ml.embeddings import get_embedding_provider
from backend.app.ml.preprocessing import extract_linguistic_signals
from backend.app.evaluation.metrics import compute_comprehensive_metrics
from backend.app.schemas.model_schema import (
    ModelSummary,
    ModelTrainRequest,
    ModelCardResponse
)
from backend.app.services.dataset_service import dataset_service

router = APIRouter(prefix="/models", tags=["Model Registry & Training"])


@router.get("", response_model=List[ModelSummary])
async def list_models_endpoint():
    """List all available models in the registry."""
    return model_registry.list_models()


@router.get("/{name}/card", response_model=ModelCardResponse)
async def get_model_card_endpoint(name: str):
    """Retrieve full research Model Card for a model architecture."""
    card = model_registry.get_model_card(name)
    if "error" in card:
        raise HTTPException(status_code=404, detail=card["error"])
    return ModelCardResponse(
        model_name=card["model_name"],
        architecture=card["architecture"],
        description=card["description"],
        dataset=card.get("dataset", "ISOT Fake News Dataset"),
        training_status=card.get("training_status", "Ready"),
        created_at=card.get("created_at", ""),
        metrics=card.get("metrics", {}),
        intended_use=card.get("intended_use", ""),
        limitations=card.get("limitations", "")
    )


@router.post("/active")
async def set_active_model_endpoint(payload: Dict[str, str]):
    """Switch active inference model."""
    name = payload.get("model_name", "")
    try:
        active = model_registry.set_active_model(name)
        return {"status": "success", "active_model": active}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/train")
async def train_model_endpoint(payload: ModelTrainRequest):
    """
    Train a selected model architecture (TF-IDF + LogisticRegression, TF-IDF + LinearSVM,
    PassiveAggressive, or VeritasFusion) on the news corpus.
    """
    model_name = payload.model_name
    if model_name not in model_registry.models:
        raise HTTPException(status_code=400, detail=f"Unknown model architecture: {model_name}")

    # Load training data
    data_path = settings.BASE_PATH / "fake_news_data.csv"
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Dataset 'fake_news_data.csv' not found for training.")

    logger.info(f"Loading training data from {data_path.name}...")
    df = pd.read_csv(data_path, low_memory=False)
    
    # Subsample for CPU execution
    limit = min(payload.sample_limit or 2000, len(df))
    sub_df = df.sample(n=limit, random_state=42).reset_index(drop=True)
    
    # Normalize labels
    sub_df["label_int"] = dataset_service.normalize_labels(sub_df["label"])
    texts = sub_df["text"].fillna("").astype(str).tolist()
    labels = sub_df["label_int"].tolist()

    # Train / Test split (80/20)
    split_idx = int(len(texts) * 0.8)
    train_texts, test_texts = texts[:split_idx], texts[split_idx:]
    train_labels, test_labels = labels[:split_idx], labels[split_idx:]

    model_instance = model_registry.models[model_name]
    start_time = time.time()

    if model_name == "VeritasFusion":
        embedder = get_embedding_provider()
        train_embs = embedder.embed_batch(train_texts)
        test_embs = embedder.embed_batch(test_texts)
        
        train_ling = [extract_linguistic_signals(t) for t in train_texts]
        test_ling = [extract_linguistic_signals(t) for t in test_texts]

        model_instance.train(train_embs, train_ling, train_labels)
        
        # Evaluate on test split
        preds = []
        probs = []
        for i in range(len(test_texts)):
            res = model_instance.predict_multimodal(test_embs[i], test_ling[i])
            pred_lbl = 1 if res["verdict"] == "LIKELY_FAKE" else 0
            preds.append(pred_lbl)
            probs.append(res["raw_fake_probability"])
    else:
        # Classical TF-IDF Baselines
        model_instance.train(train_texts, train_labels)
        preds = model_instance.predict(test_texts).tolist()
        probs = model_instance.predict_proba(test_texts)[:, 1].tolist()

    train_duration = round(time.time() - start_time, 2)
    metrics = compute_comprehensive_metrics(test_labels, preds, probs)
    metrics["training_time_seconds"] = train_duration
    metrics["sample_count"] = len(texts)

    # Save model checkpoint and update Model Card
    model_registry.save_checkpoint(model_name)
    model_registry.update_metrics(model_name, metrics)

    logger.info(f"Model '{model_name}' trained in {train_duration}s. Test Macro F1: {metrics['macro_f1']}")

    return {
        "status": "success",
        "model_name": model_name,
        "training_time_s": train_duration,
        "metrics": metrics
    }
