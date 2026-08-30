import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.config import settings
from backend.app.core.error_handlers import VeritasException
from backend.app.database.database import get_db
from backend.app.database.db_models import AnalysisRecord
from backend.app.schemas.analysis_schema import (
    TextAnalysisRequest,
    UrlAnalysisRequest,
    AnalysisResponse,
    ClaimItem,
    EvidenceItem,
    ModalityBreakdown,
    NarrativeConsistencyData
)
from backend.app.services.pipeline_service import pipeline_service
from backend.app.services.url_scraper_service import scrape_article_from_url

router = APIRouter(prefix="/analyze", tags=["Verification & Analysis"])


@router.post("/text", response_model=AnalysisResponse)
async def analyze_text_endpoint(
    payload: TextAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyze plain article text or claim assertion."""
    return await pipeline_service.execute_verification(
        text=payload.text,
        title=payload.title,
        category=payload.category or "General",
        inference_mode=payload.inference_mode or settings.DEFAULT_INFERENCE_MODE,
        db_session=db
    )


@router.post("/url", response_model=AnalysisResponse)
async def analyze_url_endpoint(
    payload: UrlAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Scrape news article from URL and perform end-to-end verification."""
    scraped = scrape_article_from_url(payload.url)
    return await pipeline_service.execute_verification(
        text=scraped["text"],
        title=scraped["title"],
        source_url=scraped["url"],
        category=payload.category or "General",
        inference_mode=payload.inference_mode or settings.DEFAULT_INFERENCE_MODE,
        db_session=db
    )


@router.post("/multimodal", response_model=AnalysisResponse)
async def analyze_multimodal_endpoint(
    text: str = Form(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form("General"),
    inference_mode: Optional[str] = Form("BALANCED"),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """Analyze multimodal content with optional image upload and OCR extraction."""
    image_path = None
    if image:
        # Validate extension
        ext = image.filename.split(".")[-1].lower() if "." in image.filename else ""
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise VeritasException(
                f"Invalid image extension '{ext}'. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}",
                status_code=400
            )

        saved_name = f"upload_{int(os.times().elapsed*1000)}_{image.filename}"
        image_path = settings.UPLOADS_PATH / saved_name
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

    return await pipeline_service.execute_verification(
        text=text,
        title=title,
        image_path=image_path,
        category=category or "General",
        inference_mode=inference_mode or settings.DEFAULT_INFERENCE_MODE,
        db_session=db
    )


@router.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    limit: int = 15,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve recent verification analyses history."""
    stmt = select(AnalysisRecord).order_by(desc(AnalysisRecord.created_at)).limit(limit)
    res = await db.execute(stmt)
    records = res.scalars().all()

    results = []
    for r in records:
        results.append(AnalysisResponse(
            id=r.id,
            verdict=r.verdict,
            confidence=r.confidence,
            calibrated_confidence=r.calibrated_confidence,
            evidence_strength=r.evidence_strength or "Moderate",
            reliability=r.reliability or "Moderate",
            inference_mode=r.inference_mode or "BALANCED",
            latency_ms=r.latency_ms or 0.0,
            title=r.title,
            content_preview=(r.content[:200] + "...") if r.content else "",
            source_url=r.source_url,
            image_filename=r.image_filename,
            modality_breakdown=ModalityBreakdown(**(r.modality_breakdown or {"text_percentage": 100.0, "image_percentage": 0.0, "evidence_percentage": 0.0})),
            key_reasons=r.key_reasons or [],
            claims=[ClaimItem(**c) for c in (r.claims or [])],
            supporting_evidence=[],
            contradicting_evidence=[],
            related_evidence=[],
            narrative_consistency=NarrativeConsistencyData(**(r.narrative_consistency or {"consistent_pct": 0.33, "contradictory_pct": 0.33, "novel_pct": 0.34, "dominant_narrative": "Unindexed", "similarity_spread": 0.0, "similar_narratives": []})),
            linguistic_signals=r.linguistic_signals or {},
            image_signals=r.image_signals or {},
            token_attributions=r.token_attributions or [],
            limitations=r.limitations or [],
            created_at=r.created_at.isoformat() if r.created_at else None
        ))
    return results


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_by_id(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full analysis report by ID."""
    stmt = select(AnalysisRecord).where(AnalysisRecord.id == analysis_id)
    res = await db.execute(stmt)
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail=f"Analysis with id {analysis_id} not found.")

    return AnalysisResponse(
        id=r.id,
        verdict=r.verdict,
        confidence=r.confidence,
        calibrated_confidence=r.calibrated_confidence,
        evidence_strength=r.evidence_strength or "Moderate",
        reliability=r.reliability or "Moderate",
        inference_mode=r.inference_mode or "BALANCED",
        latency_ms=r.latency_ms or 0.0,
        title=r.title,
        content_preview=r.content,
        source_url=r.source_url,
        image_filename=r.image_filename,
        modality_breakdown=ModalityBreakdown(**(r.modality_breakdown or {"text_percentage": 100.0, "image_percentage": 0.0, "evidence_percentage": 0.0})),
        key_reasons=r.key_reasons or [],
        claims=[ClaimItem(**c) for c in (r.claims or [])],
        supporting_evidence=[],
        contradicting_evidence=[],
        related_evidence=[],
        narrative_consistency=NarrativeConsistencyData(**(r.narrative_consistency or {"consistent_pct": 0.33, "contradictory_pct": 0.33, "novel_pct": 0.34, "dominant_narrative": "Unindexed", "similarity_spread": 0.0, "similar_narratives": []})),
        linguistic_signals=r.linguistic_signals or {},
        image_signals=r.image_signals or {},
        token_attributions=r.token_attributions or [],
        limitations=r.limitations or [],
        created_at=r.created_at.isoformat() if r.created_at else None
    )
