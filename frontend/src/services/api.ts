import {
  AnalysisResponse,
  ModelSummary,
  DatasetSummary,
  SystemStatus,
  EvidenceItem
} from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

export const api = {
  // Verification
  analyzeText: async (payload: {
    text: string;
    title?: string;
    category?: string;
    inference_mode?: string;
  }): Promise<AnalysisResponse> => {
    const res = await fetch(`${API_BASE}/analyze/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.details || 'Verification analysis failed.');
    }
    return res.json();
  },

  analyzeUrl: async (payload: {
    url: string;
    category?: string;
    inference_mode?: string;
  }): Promise<AnalysisResponse> => {
    const res = await fetch(`${API_BASE}/analyze/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.details || 'URL scraping/analysis failed.');
    }
    return res.json();
  },

  analyzeMultimodal: async (formData: FormData): Promise<AnalysisResponse> => {
    const res = await fetch(`${API_BASE}/analyze/multimodal`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.details || 'Multimodal analysis failed.');
    }
    return res.json();
  },

  getHistory: async (limit: number = 15): Promise<AnalysisResponse[]> => {
    const res = await fetch(`${API_BASE}/analyze/history?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch analysis history.');
    return res.json();
  },

  // System & Telemetry
  getSystemStatus: async (): Promise<SystemStatus> => {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error('Failed to fetch system status.');
    return res.json();
  },

  setInferenceMode: async (mode: string): Promise<{ status: string; active_mode: string }> => {
    const res = await fetch(`${API_BASE}/system/mode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode }),
    });
    if (!res.ok) throw new Error('Failed to switch inference mode.');
    return res.json();
  },

  // Models
  listModels: async (): Promise<ModelSummary[]> => {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to list models.');
    return res.json();
  },

  setActiveModel: async (modelName: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/models/active`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_name: modelName }),
    });
    if (!res.ok) throw new Error('Failed to set active model.');
    return res.json();
  },

  trainModel: async (payload: { model_name: string; sample_limit?: number }): Promise<any> => {
    const res = await fetch(`${API_BASE}/models/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || err.details || 'Model training failed.');
    }
    return res.json();
  },

  getModelCard: async (name: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/models/${name}/card`);
    if (!res.ok) throw new Error('Failed to fetch model card.');
    return res.json();
  },

  // Evidence
  listEvidence: async (category?: string): Promise<EvidenceItem[]> => {
    const url = category && category !== 'All' ? `${API_BASE}/evidence?category=${category}` : `${API_BASE}/evidence`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch evidence.');
    return res.json();
  },

  seedEvidence: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/evidence/seed`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to seed evidence.');
    return res.json();
  },

  // Datasets
  listDatasets: async (): Promise<DatasetSummary[]> => {
    const res = await fetch(`${API_BASE}/datasets`);
    if (!res.ok) throw new Error('Failed to list datasets.');
    return res.json();
  },

  // Evaluations & Experiments
  runEvaluation: async (payload: { model_name: string; sample_limit: number }): Promise<any> => {
    const res = await fetch(`${API_BASE}/evaluations/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Evaluation failed.');
    return res.json();
  },

  runCrossDomain: async (payload: { train_domain: string; test_domain: string; sample_limit: number }): Promise<any> => {
    const res = await fetch(`${API_BASE}/evaluations/cross-domain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Cross-domain evaluation failed.');
    return res.json();
  },

  runAdversarial: async (payload: { model_name: string; sample_limit: number }): Promise<any> => {
    const res = await fetch(`${API_BASE}/evaluations/adversarial`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Adversarial evaluation failed.');
    return res.json();
  },

  runAblation: async (sampleLimit: number = 250): Promise<any> => {
    const res = await fetch(`${API_BASE}/experiments/ablation?sample_limit=${sampleLimit}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Ablation run failed.');
    return res.json();
  },
};
