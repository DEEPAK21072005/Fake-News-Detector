from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class DatasetSummaryResponse(BaseModel):
    id: int
    name: str
    filename: str
    row_count: int
    columns: List[str]
    mapped_columns: Dict[str, str]
    split_info: Dict[str, Any]
    created_at: str


class DatasetSplitRequest(BaseModel):
    train_ratio: float = Field(0.70, ge=0.1, le=0.9)
    val_ratio: float = Field(0.15, ge=0.05, le=0.5)
    test_ratio: float = Field(0.15, ge=0.05, le=0.5)
    stratify: bool = True
    group_by_narrative: bool = False


class DatasetPreviewResponse(BaseModel):
    dataset_id: int
    name: str
    total_rows: int
    columns: List[str]
    preview_rows: List[Dict[str, Any]]
    detected_mappings: Dict[str, str]
