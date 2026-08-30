from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ModelSummary(BaseModel):
    name: str
    architecture: str
    is_active: bool
    is_trained: bool
    metrics: Dict[str, Any]
    intended_use: str


class ModelTrainRequest(BaseModel):
    model_name: str = Field(..., description="TFIDF_LogisticRegression | TFIDF_LinearSVM | PassiveAggressive | VeritasFusion")
    dataset_name: Optional[str] = "ISOT / fake_news_data.csv"
    sample_limit: Optional[int] = Field(2000, description="Max samples to train on for CPU execution.")
    hyperparameters: Optional[Dict[str, Any]] = None


class ModelCardResponse(BaseModel):
    model_name: str
    architecture: str
    description: str
    dataset: str
    training_status: str
    created_at: str
    metrics: Dict[str, Any]
    intended_use: str
    limitations: str
