from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class EvaluationRunRequest(BaseModel):
    model_name: str = "VeritasFusion"
    sample_limit: int = Field(500, description="Test sample evaluation limit.")
    dataset_name: Optional[str] = "fake_news_data.csv"


class CrossDomainRequest(BaseModel):
    train_domain: str = "politicsNews"
    test_domain: str = "worldnews"
    sample_limit: int = Field(500, description="Samples per domain.")


class AdversarialTestRequest(BaseModel):
    model_name: str = "TFIDF_LogisticRegression"
    sample_limit: int = Field(200, description="Number of samples to perturb.")
