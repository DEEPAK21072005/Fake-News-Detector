from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import pandas as pd

from backend.app.core.config import settings
from backend.app.database.database import get_db
from backend.app.database.db_models import ExperimentLogRecord, AblationRecord
from backend.app.evaluation.ablation import ablation_runner
from backend.app.services.dataset_service import dataset_service

router = APIRouter(prefix="/experiments", tags=["Experiments & Ablations"])


@router.get("")
async def list_experiments_endpoint(db: AsyncSession = Depends(get_db)):
    """List historical experiment logs and ablation runs."""
    stmt = select(AblationRecord).order_by(desc(AblationRecord.created_at))
    res = await db.execute(stmt)
    records = res.scalars().all()
    
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "experiment_id": r.experiment_id,
            "configuration": r.configuration_name,
            "modalities": r.modalities,
            "macro_f1": r.macro_f1,
            "accuracy": r.accuracy,
            "notes": r.notes,
            "created_at": r.created_at.isoformat() if r.created_at else ""
        })
    return results


@router.post("/ablation")
async def run_ablation_study_endpoint(sample_limit: int = 300, db: AsyncSession = Depends(get_db)):
    """Run systematic ablation study across all multimodal configurations."""
    data_path = settings.BASE_PATH / "fake_news_data.csv"
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Dataset fake_news_data.csv not found.")

    df = pd.read_csv(data_path, low_memory=False)
    limit = min(sample_limit, len(df))
    sub_df = df.sample(n=limit, random_state=42).reset_index(drop=True)
    sub_df["label_int"] = dataset_service.normalize_labels(sub_df["label"])

    texts = sub_df["text"].fillna("").tolist()
    labels = sub_df["label_int"].tolist()

    ablation_results = ablation_runner.run_ablation_suite(texts, labels, sample_limit=sample_limit)

    # Save to database
    exp_id = f"exp_ablation_{int(pd.Timestamp.now().timestamp())}"
    for res in ablation_results:
        rec = AblationRecord(
            experiment_id=exp_id,
            configuration_name=res["configuration"],
            modalities=res["modalities"],
            macro_f1=res["macro_f1"],
            accuracy=res["accuracy"],
            precision=res.get("precision", res["accuracy"]),
            recall=res.get("recall", res["macro_f1"]),
            notes=res["notes"]
        )
        db.add(rec)
    await db.commit()

    return {
        "experiment_id": exp_id,
        "sample_size": limit,
        "results": ablation_results
    }
