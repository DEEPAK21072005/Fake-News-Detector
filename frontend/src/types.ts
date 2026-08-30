export type VerdictType = 'LIKELY_REAL' | 'LIKELY_FAKE' | 'UNCERTAIN' | 'INSUFFICIENT_EVIDENCE';

export interface ClaimItem {
  claim_id: number;
  text: string;
  confidence: number;
  is_title_claim: boolean;
  type: string;
}

export interface EvidenceItem {
  id?: number;
  title: string;
  text: string;
  source: string;
  url?: string;
  publication_date?: string;
  domain: string;
  similarity: number;
  credibility_score: number;
  adjusted_score: number;
  stance: string;
  category: string;
}

export interface ModalityBreakdown {
  text_percentage: number;
  image_percentage: number;
  evidence_percentage: number;
}

export interface NarrativeConsistencyData {
  consistent_pct: number;
  contradictory_pct: number;
  novel_pct: number;
  dominant_narrative: string;
  similarity_spread: number;
  similar_narratives: Array<{
    title: string;
    source: string;
    similarity: number;
    stance: string;
  }>;
}

export interface TokenAttribution {
  token: string;
  score: number;
  polarity: 'Fake-indicative' | 'Real-indicative';
  reasons: string[];
}

export interface LinguisticSignals {
  sensationalism_score: number;
  clickbait_score: number;
  uppercase_ratio: number;
  punctuation_anomaly_score: number;
  sentiment_polarity: number;
  emotional_intensity: number;
  lexical_diversity_ttr: number;
  average_sentence_length: number;
  total_words: number;
  total_sentences: number;
  clickbait_indicators_found: string[];
  sensational_keywords_found: string[];
}

export interface AnalysisResponse {
  id?: number;
  verdict: VerdictType;
  confidence: number;
  calibrated_confidence: number;
  evidence_strength: 'Strong' | 'Moderate' | 'Weak' | 'None';
  reliability: 'High' | 'Moderate' | 'Low';
  inference_mode: string;
  latency_ms: number;
  title?: string;
  content_preview: string;
  source_url?: string;
  image_filename?: string;
  modality_breakdown: ModalityBreakdown;
  key_reasons: string[];
  claims: ClaimItem[];
  supporting_evidence: EvidenceItem[];
  contradicting_evidence: EvidenceItem[];
  related_evidence: EvidenceItem[];
  narrative_consistency: NarrativeConsistencyData;
  linguistic_signals: LinguisticSignals;
  image_signals: Record<string, any>;
  token_attributions: TokenAttribution[];
  llm_synthesis?: {
    provider: string;
    summary: string;
    claim_analysis: string;
    evidence_synthesis: string;
  };
  limitations: string[];
  created_at?: string;
}

export interface ModelSummary {
  name: string;
  architecture: string;
  is_active: boolean;
  is_trained: boolean;
  metrics: Record<string, any>;
  intended_use: string;
}

export interface DatasetSummary {
  id: number;
  name: string;
  filename: string;
  row_count: number;
  columns: string[];
  mapped_columns: Record<string, string>;
  split_info: Record<string, any>;
  created_at: string;
}

export interface SystemStatus {
  status: string;
  app_name: string;
  environment: string;
  inference_mode: string;
  backend: string;
  database: string;
  text_model: string;
  vision_engine: string;
  vector_store: {
    status: string;
    indexed_documents: number;
  };
  llm_provider: {
    provider: string;
    configured: boolean;
  };
  hardware: {
    os: string;
    processor: string;
    cpu_cores: number;
    total_ram_gb: number;
    available_ram_gb: number;
    ram_usage_percent: number;
    cuda_available: boolean;
    gpu_name: string;
    recommended_profile: string;
    active_mode: string;
  };
  loaded_models_count: number;
}
