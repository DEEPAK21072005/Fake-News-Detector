import time
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.core.security import sanitize_text
from backend.app.database.db_models import AnalysisRecord
from backend.app.ml.preprocessing import (
    extract_linguistic_signals,
    extract_claims,
    clean_text_basic
)
from backend.app.ml.embeddings import get_embedding_provider
from backend.app.ml.vision_ocr import extract_visual_features, extract_ocr_text
from backend.app.ml.model_registry import model_registry
from backend.app.retrieval.evidence_engine import evidence_engine
from backend.app.retrieval.narrative_engine import narrative_engine
from backend.app.explainability.explainer import prediction_explainer
from backend.app.explainability.llm_explainer import get_llm_provider
from backend.app.schemas.analysis_schema import (
    AnalysisResponse,
    ClaimItem,
    EvidenceItem,
    ModalityBreakdown,
    NarrativeConsistencyData
)


class VerificationPipelineService:
    """
    Core VeritasAI Multimodal Verification Pipeline.
    Orchestrates the 8-stage verification lifecycle.
    """
    def __init__(self):
        self.embedding_provider = get_embedding_provider()
        self.llm_provider = get_llm_provider()

    async def execute_verification(
        self,
        text: str,
        title: Optional[str] = None,
        source_url: Optional[str] = None,
        image_path: Optional[Path] = None,
        category: str = "General",
        inference_mode: str = "BALANCED",
        db_session: Optional[AsyncSession] = None
    ) -> AnalysisResponse:
        start_time = time.time()
        logger.info(f"Initiating VeritasAI verification pipeline (mode: {inference_mode})...")

        # Stage 1: Preprocessing & Input Sanitization
        clean_body = sanitize_text(text, max_chars=settings.MAX_SCRAPED_CHARS)
        clean_title = sanitize_text(title or "", max_chars=500)
        
        # Stage 2: Linguistic Stylometry & Emotional Signals
        linguistic_signals = extract_linguistic_signals(clean_body, clean_title)

        # Stage 3: Claim Extraction
        raw_claims = extract_claims(clean_body, clean_title, max_claims=4)
        claims = [ClaimItem(**c) for c in raw_claims]
        primary_claim_text = claims[0].text if claims else (clean_title or clean_body[:200])

        # Stage 4: Text Semantic Embeddings & Vision/OCR
        text_embedding = self.embedding_provider.embed_text(f"{clean_title}. {clean_body}".strip())

        image_signals = {}
        ocr_embedding = None
        has_image = False

        if image_path and image_path.exists():
            has_image = True
            logger.info(f"Analyzing multimodal image: {image_path.name}")
            image_signals = extract_visual_features(image_path)
            
            if settings.ENABLE_OCR:
                ocr_result = extract_ocr_text(image_path)
                ocr_text = ocr_result.get("extracted_text", "")
                if ocr_text:
                    image_signals["ocr_detected_text"] = ocr_text
                    ocr_embedding = self.embedding_provider.embed_text(ocr_text)

        # Stage 5: Evidence Retrieval & Stance Alignment
        # Search evidence base using the primary extracted claim
        evidence_results = evidence_engine.verify_claim(primary_claim_text, top_k=6)
        
        supporting_items = [EvidenceItem(**e) for e in evidence_results.get("supporting_evidence", [])]
        contradicting_items = [EvidenceItem(**e) for e in evidence_results.get("contradicting_evidence", [])]
        related_items = [EvidenceItem(**e) for e in evidence_results.get("related_evidence", [])]

        # Stage 6: Cross-Instance Narrative Consistency Analysis
        narrative_results = narrative_engine.analyze_narrative_consistency(primary_claim_text)
        narrative_data = NarrativeConsistencyData(**narrative_results)

        # Stage 7: Multimodal Fusion & Confidence Calibration
        active_model = model_registry.get_active_model()
        if hasattr(active_model, "predict_multimodal"):
            fusion_results = active_model.predict_multimodal(
                text_embedding=text_embedding,
                linguistic_signals=linguistic_signals,
                image_features=image_signals if has_image else None,
                ocr_embedding=ocr_embedding,
                retrieval_signals=evidence_results,
                narrative_signals=narrative_results
            )
        else:
            # Baseline text model fallback
            raw_prob = float(active_model.predict_proba([clean_body])[0, 1])
            is_fake = raw_prob >= 0.5
            fusion_results = {
                "verdict": "LIKELY_FAKE" if is_fake else "LIKELY_REAL",
                "confidence": round(raw_prob if is_fake else 1.0 - raw_prob, 2),
                "calibrated_confidence": round(raw_prob if is_fake else 1.0 - raw_prob, 2),
                "evidence_strength": evidence_results.get("evidence_strength", "Moderate"),
                "reliability": "Moderate",
                "modality_breakdown": {"text_percentage": 100.0, "image_percentage": 0.0, "evidence_percentage": 0.0},
                "key_reasons": ["Classification derived from statistical text baseline."],
            }

        # Stage 8: Explainability & LLM Synthesis
        token_attributions = prediction_explainer.explain_text_signals(clean_body, linguistic_signals, top_k=12)
        limitations = prediction_explainer.generate_limitations(
            verdict=fusion_results["verdict"],
            evidence_strength=fusion_results["evidence_strength"],
            has_image=has_image
        )

        llm_synthesis = None
        if inference_mode in ("RESEARCH", "CLOUD_ENHANCED") or settings.LLM_PROVIDER != "null":
            try:
                llm_synthesis = await self.llm_provider.synthesize_explanation(
                    claim=primary_claim_text,
                    verdict=fusion_results["verdict"],
                    confidence=fusion_results["calibrated_confidence"],
                    key_reasons=fusion_results["key_reasons"],
                    supporting_evidence=evidence_results.get("supporting_evidence", []),
                    contradicting_evidence=evidence_results.get("contradicting_evidence", [])
                )
            except Exception as e:
                logger.warning(f"LLM explanation synthesis skipped: {e}")

        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Verification finished in {latency_ms} ms. Verdict: {fusion_results['verdict']} ({int(fusion_results['calibrated_confidence']*100)}%)")

        response = AnalysisResponse(
            verdict=fusion_results["verdict"],
            confidence=fusion_results["confidence"],
            calibrated_confidence=fusion_results["calibrated_confidence"],
            evidence_strength=fusion_results["evidence_strength"],
            reliability=fusion_results["reliability"],
            inference_mode=inference_mode,
            latency_ms=latency_ms,
            title=clean_title or (clean_body[:80] + "..."),
            content_preview=clean_body[:300] + ("..." if len(clean_body) > 300 else ""),
            source_url=source_url,
            image_filename=image_path.name if image_path else None,
            modality_breakdown=ModalityBreakdown(**fusion_results["modality_breakdown"]),
            key_reasons=fusion_results["key_reasons"],
            claims=claims,
            supporting_evidence=supporting_items,
            contradicting_evidence=contradicting_items,
            related_evidence=related_items,
            narrative_consistency=narrative_data,
            linguistic_signals=linguistic_signals,
            image_signals=image_signals,
            token_attributions=token_attributions,
            llm_synthesis=llm_synthesis,
            limitations=limitations,
            created_at=datetime.datetime.utcnow().isoformat()
        )

        # Persist analysis to database if session provided
        if db_session:
            try:
                record = AnalysisRecord(
                    input_type="url" if source_url else ("multimodal" if has_image else "text"),
                    title=response.title,
                    content=clean_body,
                    source_url=source_url,
                    image_filename=image_path.name if image_path else None,
                    verdict=response.verdict,
                    confidence=response.confidence,
                    calibrated_confidence=response.calibrated_confidence,
                    evidence_strength=response.evidence_strength,
                    reliability=response.reliability,
                    inference_mode=response.inference_mode,
                    latency_ms=response.latency_ms,
                    modality_breakdown=response.modality_breakdown.dict(),
                    key_reasons=response.key_reasons,
                    claims=[c.dict() for c in response.claims],
                    retrieved_evidence=[e.dict() for e in supporting_items + contradicting_items + related_items],
                    narrative_consistency=response.narrative_consistency.dict(),
                    linguistic_signals=response.linguistic_signals,
                    image_signals=response.image_signals,
                    token_attributions=response.token_attributions,
                    limitations=response.limitations
                )
                db_session.add(record)
                await db_session.commit()
                await db_session.refresh(record)
                response.id = record.id
            except Exception as e:
                logger.warning(f"Could not persist analysis record to DB: {e}")

        return response


pipeline_service = VerificationPipelineService()
