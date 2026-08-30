from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Article body or claim text to analyze.")
    title: Optional[str] = Field(None, description="Optional article headline or claim title.")
    source: Optional[str] = Field(None, description="Optional source or author metadata.")
    category: Optional[str] = Field("General", description="Subject area: Politics, Health, Science, Tech, World.")
    inference_mode: Optional[str] = Field("BALANCED", description="FAST | BALANCED | RESEARCH | CLOUD_ENHANCED")


class UrlAnalysisRequest(BaseModel):
    url: str = Field(..., description="Target news article URL to scrape and analyze.")
    category: Optional[str] = Field("General", description="Subject area.")
    inference_mode: Optional[str] = Field("BALANCED", description="Inference mode.")


class ClaimItem(BaseModel):
    claim_id: int
    text: str
    confidence: float
    is_title_claim: bool
    type: str


class EvidenceItem(BaseModel):
    id: Optional[int] = None
    title: str
    text: str
    source: str
    url: Optional[str] = None
    publication_date: Optional[str] = None
    domain: str
    similarity: float
    credibility_score: float
    adjusted_score: float
    stance: str
    category: str


class ModalityBreakdown(BaseModel):
    text_percentage: float
    image_percentage: float
    evidence_percentage: float


class NarrativeConsistencyData(BaseModel):
    consistent_pct: float
    contradictory_pct: float
    novel_pct: float
    dominant_narrative: str
    similarity_spread: float
    similar_narratives: List[Dict[str, Any]] = []


class AnalysisResponse(BaseModel):
    id: Optional[int] = None
    verdict: str  # LIKELY_REAL | LIKELY_FAKE | UNCERTAIN | INSUFFICIENT_EVIDENCE
    confidence: float
    calibrated_confidence: float
    evidence_strength: str  # Strong | Moderate | Weak | None
    reliability: str  # High | Moderate | Low
    inference_mode: str
    latency_ms: float
    title: Optional[str] = None
    content_preview: str
    source_url: Optional[str] = None
    image_filename: Optional[str] = None
    
    modality_breakdown: ModalityBreakdown
    key_reasons: List[str]
    claims: List[ClaimItem]
    supporting_evidence: List[EvidenceItem]
    contradicting_evidence: List[EvidenceItem]
    related_evidence: List[EvidenceItem]
    narrative_consistency: NarrativeConsistencyData
    linguistic_signals: Dict[str, Any]
    image_signals: Dict[str, Any]
    token_attributions: List[Dict[str, Any]]
    llm_synthesis: Optional[Dict[str, Any]] = None
    limitations: List[str]
    created_at: Optional[str] = None
