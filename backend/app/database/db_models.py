import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, JSON
from backend.app.database.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    input_type = Column(String(32), default="text")  # text | url | multimodal
    title = Column(String(512), nullable=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(1024), nullable=True)
    image_filename = Column(String(512), nullable=True)
    
    # Verdicts & Confidence
    verdict = Column(String(64), nullable=False)  # LIKELY_REAL | LIKELY_FAKE | UNCERTAIN | INSUFFICIENT_EVIDENCE
    confidence = Column(Float, nullable=False)
    calibrated_confidence = Column(Float, nullable=False)
    evidence_strength = Column(String(32), default="Moderate")  # Strong | Moderate | Weak | None
    reliability = Column(String(32), default="Moderate")  # High | Moderate | Low
    inference_mode = Column(String(32), default="BALANCED")
    latency_ms = Column(Float, default=0.0)

    # Detailed Structured JSON Artifacts
    modality_breakdown = Column(JSON, default=dict)
    key_reasons = Column(JSON, default=list)
    claims = Column(JSON, default=list)
    retrieved_evidence = Column(JSON, default=list)
    narrative_consistency = Column(JSON, default=dict)
    linguistic_signals = Column(JSON, default=dict)
    image_signals = Column(JSON, default=dict)
    token_attributions = Column(JSON, default=list)
    limitations = Column(JSON, default=list)


class ModelCheckpointRecord(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(128), unique=True, nullable=False, index=True)
    architecture = Column(String(128), nullable=False)  # TFIDF_LR | TFIDF_SVM | VeritasFusion | DistilBERT
    version = Column(String(32), default="1.0.0")
    dataset_name = Column(String(128), default="ISOT / FakeNewsCorpus")
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Performance Metrics
    accuracy = Column(Float, nullable=True)
    macro_f1 = Column(Float, nullable=True)
    weighted_f1 = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)
    calibration_error = Column(Float, nullable=True)
    
    metrics_json = Column(JSON, default=dict)
    hyperparameters = Column(JSON, default=dict)
    model_card = Column(JSON, default=dict)
    checkpoint_path = Column(String(512), nullable=True)


class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False, index=True)
    filename = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    row_count = Column(Integer, default=0)
    columns = Column(JSON, default=list)
    mapped_columns = Column(JSON, default=dict)
    split_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class EvidenceItemRecord(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    text = Column(Text, nullable=False)
    source = Column(String(256), nullable=False)
    url = Column(String(1024), nullable=True)
    publication_date = Column(String(64), nullable=True)
    domain = Column(String(128), nullable=True)
    language = Column(String(16), default="en")
    credibility_score = Column(Float, default=0.9)  # 0.0 to 1.0 based on domain authority
    category = Column(String(64), default="General")  # Politics | Health | Science | Tech | World
    stance_tag = Column(String(64), default="Supporting")  # Supporting | Contradicting | Context
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ExperimentLogRecord(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String(128), nullable=False)
    model_name = Column(String(128), nullable=False)
    dataset_name = Column(String(128), nullable=False)
    features_used = Column(JSON, default=list)
    hyperparameters = Column(JSON, default=dict)
    training_time_s = Column(Float, default=0.0)
    inference_time_ms = Column(Float, default=0.0)
    metrics = Column(JSON, default=dict)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AblationRecord(Base):
    __tablename__ = "ablations"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), index=True)
    configuration_name = Column(String(128), nullable=False)  # e.g. Text Only, Text+Image, Full VeritasFusion
    modalities = Column(JSON, default=list)
    macro_f1 = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=True)
    notes = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
