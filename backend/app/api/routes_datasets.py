import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.config import settings
from backend.app.core.error_handlers import VeritasException
from backend.app.database.database import get_db
from backend.app.database.db_models import DatasetRecord
from backend.app.schemas.dataset_schema import (
    DatasetSummaryResponse,
    DatasetSplitRequest,
    DatasetPreviewResponse
)
from backend.app.services.dataset_service import dataset_service

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])


@router.post("/upload", response_model=DatasetSummaryResponse)
async def upload_dataset_endpoint(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload custom research dataset (CSV/JSON/JSONL), parse columns, and register in database."""
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ("csv", "json", "jsonl"):
        raise VeritasException(f"Unsupported format '{ext}'. Upload CSV, JSON, or JSONL.", status_code=400)

    saved_path = settings.DATA_PATH / "uploads" / f"{name.replace(' ', '_')}_{file.filename}"
    with open(saved_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    df, mappings = dataset_service.load_dataset_file(saved_path)

    record = DatasetRecord(
        name=name,
        filename=file.filename,
        file_path=str(saved_path),
        row_count=len(df),
        columns=df.columns.tolist(),
        mapped_columns=mappings,
        split_info={"status": "Unsplit", "train": 0, "val": 0, "test": 0}
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return DatasetSummaryResponse(
        id=record.id,
        name=record.name,
        filename=record.filename,
        row_count=record.row_count,
        columns=record.columns,
        mapped_columns=record.mapped_columns,
        split_info=record.split_info,
        created_at=record.created_at.isoformat()
    )


@router.get("", response_model=List[DatasetSummaryResponse])
async def list_datasets_endpoint(db: AsyncSession = Depends(get_db)):
    """List all registered research datasets."""
    stmt = select(DatasetRecord).order_by(desc(DatasetRecord.created_at))
    res = await db.execute(stmt)
    records = res.scalars().all()

    # Also check if root fake_news_data.csv exists and add as built-in if not in DB
    builtin_path = settings.BASE_PATH / "fake_news_data.csv"
    results = []
    for r in records:
        results.append(DatasetSummaryResponse(
            id=r.id,
            name=r.name,
            filename=r.filename,
            row_count=r.row_count,
            columns=r.columns or [],
            mapped_columns=r.mapped_columns or {},
            split_info=r.split_info or {},
            created_at=r.created_at.isoformat() if r.created_at else ""
        ))
    return results


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
async def preview_dataset_endpoint(dataset_id: int, db: AsyncSession = Depends(get_db)):
    """Preview rows and column mappings for a dataset."""
    stmt = select(DatasetRecord).where(DatasetRecord.id == dataset_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    path = Path(record.file_path)
    df, mappings = dataset_service.load_dataset_file(path)
    preview = df.head(10).to_dict(orient="records")

    return DatasetPreviewResponse(
        dataset_id=record.id,
        name=record.name,
        total_rows=len(df),
        columns=df.columns.tolist(),
        preview_rows=preview,
        detected_mappings=mappings
    )


@router.post("/{dataset_id}/split")
async def split_dataset_endpoint(
    dataset_id: int,
    payload: DatasetSplitRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate leakage-free train/val/test splits."""
    stmt = select(DatasetRecord).where(DatasetRecord.id == dataset_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    path = Path(record.file_path)
    df, mappings = dataset_service.load_dataset_file(path)
    
    split_res = dataset_service.create_leakage_free_split(
        df=df,
        mappings=mappings,
        train_ratio=payload.train_ratio,
        val_ratio=payload.val_ratio,
        test_ratio=payload.test_ratio,
        stratify=payload.stratify,
        group_by_narrative=payload.group_by_narrative
    )

    record.split_info = {
        "status": "Split Ready",
        "train_samples": split_res["train_samples"],
        "val_samples": split_res["val_samples"],
        "test_samples": split_res["test_samples"],
        "split_type": split_res["split_type"],
        "class_balance": split_res["class_balance"]
    }
    await db.commit()

    return record.split_info


@router.delete("/{dataset_id}")
async def delete_dataset_endpoint(dataset_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a dataset."""
    stmt = select(DatasetRecord).where(DatasetRecord.id == dataset_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    await db.delete(record)
    await db.commit()
    return {"status": "deleted", "dataset_id": dataset_id}
