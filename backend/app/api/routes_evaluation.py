from fastapi import APIRouter, HTTPException
try:
    import pandas as pd
except ImportError:
    pd = None
import numpy as np

from backend.app.core.config import settings
from backend.app.ml.model_registry import model_registry
from backend.app.ml.embeddings import get_embedding_provider
from backend.app.ml.preprocessing import extract_linguistic_signals
from backend.app.evaluation.metrics import compute_comprehensive_metrics
from backend.app.evaluation.cross_domain import cross_domain_evaluator
from backend.app.evaluation.adversarial import adversarial_tester
from backend.app.evaluation.ablation import ablation_runner
from backend.app.services.dataset_service import dataset_service
from backend.app.schemas.evaluation_schema import (
    EvaluationRunRequest,
    CrossDomainRequest,
    AdversarialTestRequest
)

router = APIRouter(prefix="/evaluations", tags=["Evaluation & Benchmarks"])


@router.post("/run")
async def run_evaluation_endpoint(payload: EvaluationRunRequest):
    """Run full evaluation suite on a test split."""
    data_path = settings.BASE_PATH / payload.dataset_name
    if not data_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset {payload.dataset_name} not found.")

    df = pd.read_csv(data_path, low_memory=False)
    limit = min(payload.sample_limit, len(df))
    sub_df = df.sample(n=limit, random_state=42).reset_index(drop=True)

    sub_df["label_int"] = dataset_service.normalize_labels(sub_df["label"])
    texts = sub_df["text"].fillna("").astype(str).tolist()
    labels = sub_df["label_int"].tolist()

    model_name = payload.model_name
    if model_name not in model_registry.models:
        raise HTTPException(status_code=400, detail=f"Model {model_name} not found.")

    model_instance = model_registry.models[model_name]

    if model_name == "VeritasFusion":
        embedder = get_embedding_provider()
        text_embs = embedder.embed_batch(texts)
        ling_list = [extract_linguistic_signals(t) for t in texts]
        
        preds = []
        probs = []
        for i in range(len(texts)):
            res = model_instance.predict_multimodal(text_embs[i], ling_list[i])
            preds.append(1 if res["verdict"] == "LIKELY_FAKE" else 0)
            probs.append(res["raw_fake_probability"])
    else:
        preds = model_instance.predict(texts).tolist()
        probs = model_instance.predict_proba(texts)[:, 1].tolist()

    metrics = compute_comprehensive_metrics(labels, preds, probs)
    metrics["model_name"] = model_name
    metrics["dataset"] = payload.dataset_name
    metrics["samples_evaluated"] = len(texts)

    model_registry.update_metrics(model_name, metrics)
    return metrics


@router.post("/cross-domain")
async def run_cross_domain_endpoint(payload: CrossDomainRequest):
    """Evaluate performance degradation across subject domains (e.g. politics vs world news)."""
    data_path = settings.BASE_PATH / "fake_news_data.csv"
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Dataset fake_news_data.csv not found.")

    df = pd.read_csv(data_path, low_memory=False)
    df["label_int"] = dataset_service.normalize_labels(df["label"])

    if "subject" not in df.columns:
        raise HTTPException(status_code=400, detail="Dataset does not contain a 'subject' column for domain grouping.")

    # Filter domains
    train_domain_df = df[df["subject"].str.lower().str.contains(payload.train_domain.lower())].head(payload.sample_limit)
    test_domain_df = df[df["subject"].str.lower().str.contains(payload.test_domain.lower())].head(payload.sample_limit)

    if len(train_domain_df) < 20 or len(test_domain_df) < 20:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient domain samples (Found: {len(train_domain_df)} for {payload.train_domain}, {len(test_domain_df)} for {payload.test_domain})"
        )

    results = cross_domain_evaluator.evaluate_transfer(
        train_domain=payload.train_domain,
        test_domain=payload.test_domain,
        train_texts=train_domain_df["text"].fillna("").tolist(),
        train_labels=train_domain_df["label_int"].tolist(),
        test_texts=test_domain_df["text"].fillna("").tolist(),
        test_labels=test_domain_df["label_int"].tolist()
    )

    return results


@router.post("/adversarial")
async def run_adversarial_endpoint(payload: AdversarialTestRequest):
    """Run perturbation suite to test model resilience."""
    model_name = payload.model_name
    if model_name not in model_registry.models:
        raise HTTPException(status_code=400, detail=f"Model {model_name} not found.")

    model = model_registry.models[model_name]
    if not getattr(model, "is_fitted", False):
        raise HTTPException(status_code=400, detail=f"Model {model_name} must be trained before running adversarial tests.")

    data_path = settings.BASE_PATH / "fake_news_data.csv"
    df = pd.read_csv(data_path, nrows=payload.sample_limit, low_memory=False)
    df["label_int"] = dataset_service.normalize_labels(df["label"])

    res = adversarial_tester.evaluate_robustness(
        classifier=model,
        texts=df["text"].fillna("").tolist(),
        labels=df["label_int"].tolist()
    )
    res["model_name"] = model_name
    return res
