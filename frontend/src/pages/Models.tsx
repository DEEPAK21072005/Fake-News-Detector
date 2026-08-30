import React, { useState, useEffect } from 'react';
import { 
  Layers, 
  Play, 
  CheckCircle2, 
  Cpu, 
  BarChart2, 
  Info, 
  Award,
  Loader2,
  FileCode2
} from 'lucide-react';
import { api } from '../services/api';
import { ModelSummary } from '../types';

export const Models: React.FC = () => {
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [trainingModel, setTrainingModel] = useState<string | null>(null);
  const [sampleLimit, setSampleLimit] = useState(1500);
  const [selectedCard, setSelectedCard] = useState<any | null>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const fetchModels = async () => {
    try {
      const list = await api.listModels();
      setModels(list);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleTrain = async (modelName: string) => {
    setTrainingModel(modelName);
    setStatusMsg(null);
    try {
      const res = await api.trainModel({ model_name: modelName, sample_limit: sampleLimit });
      setStatusMsg(`Model ${modelName} trained successfully in ${res.training_time_s}s! Test Macro F1: ${res.metrics.macro_f1}`);
      fetchModels();
    } catch (err: any) {
      setStatusMsg(`Training error: ${err.message}`);
    } finally {
      setTrainingModel(null);
    }
  };

  const handleSetActive = async (modelName: string) => {
    try {
      await api.setActiveModel(modelName);
      fetchModels();
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleViewCard = async (modelName: string) => {
    try {
      const card = await api.getModelCard(modelName);
      setSelectedCard(card);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <Layers className="w-7 h-7 text-brand-400" />
          <span>Model Registry & Checkpoints</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Train, benchmark, and deploy statistical baselines alongside the flagship VeritasFusion multimodal engine.
        </p>
      </div>

      {/* Status Bar */}
      {statusMsg && (
        <div className="p-4 rounded-xl bg-slate-900 border border-brand-500/40 text-slate-200 text-xs flex items-center space-x-2 font-mono">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{statusMsg}</span>
        </div>
      )}

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {models.map((model) => (
          <div 
            key={model.name}
            className={`p-6 rounded-2xl bg-dark-800/90 border transition-all space-y-4 ${
              model.is_active ? 'border-brand-500 shadow-lg shadow-brand-500/10' : 'border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="text-base font-bold text-white">{model.name}</h3>
                  {model.is_active && (
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400">{model.architecture}</p>
              </div>

              <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                model.is_trained ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'
              }`}>
                {model.is_trained ? 'Trained' : 'Untrained'}
              </span>
            </div>

            {/* Metrics Snapshot */}
            <div className="grid grid-cols-3 gap-2 p-3 rounded-xl bg-dark-900/80 border border-slate-800 text-center font-mono">
              <div>
                <div className="text-[10px] text-slate-400">Macro F1</div>
                <div className="text-sm font-bold text-slate-100">
                  {model.metrics?.macro_f1 !== undefined && model.metrics?.macro_f1 !== null ? model.metrics.macro_f1 : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400">Accuracy</div>
                <div className="text-sm font-bold text-slate-100">
                  {model.metrics?.accuracy !== undefined && model.metrics?.accuracy !== null ? model.metrics.accuracy : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400">ROC-AUC</div>
                <div className="text-sm font-bold text-slate-100">
                  {model.metrics?.roc_auc !== undefined && model.metrics?.roc_auc !== null ? model.metrics.roc_auc : 'N/A'}
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-400 line-clamp-2">
              {model.intended_use}
            </p>

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 gap-2">
              <button
                onClick={() => handleViewCard(model.name)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center space-x-1"
              >
                <FileCode2 className="w-3.5 h-3.5" />
                <span>Model Card</span>
              </button>

              <div className="flex items-center space-x-2">
                {!model.is_active && (
                  <button
                    onClick={() => handleSetActive(model.name)}
                    className="px-3 py-1.5 rounded-lg bg-dark-900 border border-slate-700 hover:border-brand-500 text-slate-200 text-xs font-semibold"
                  >
                    Deploy Active
                  </button>
                )}

                <button
                  onClick={() => handleTrain(model.name)}
                  disabled={trainingModel !== null}
                  className="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold flex items-center space-x-1.5 disabled:opacity-50"
                >
                  {trainingModel === model.name ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Training...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5" />
                      <span>Train Model</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Model Card Modal */}
      {selectedCard && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-dark-800 border border-slate-700 rounded-2xl p-6 max-w-2xl w-full max-h-[85vh] overflow-y-auto space-y-4 text-xs">
            <div className="flex items-center justify-between border-b border-slate-700 pb-3">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <FileCode2 className="w-5 h-5 text-brand-400" />
                <span>Model Card: {selectedCard.model_name}</span>
              </h3>
              <button onClick={() => setSelectedCard(null)} className="text-slate-400 hover:text-white font-bold text-sm">✕</button>
            </div>

            <div className="space-y-3 text-slate-300">
              <div>
                <strong className="text-white block mb-0.5">Architecture:</strong>
                <span className="font-mono">{selectedCard.architecture}</span>
              </div>

              <div>
                <strong className="text-white block mb-0.5">Dataset & Partitioning:</strong>
                <span>{selectedCard.dataset}</span>
              </div>

              <div>
                <strong className="text-white block mb-0.5">Intended Use:</strong>
                <span>{selectedCard.intended_use}</span>
              </div>

              <div>
                <strong className="text-white block mb-0.5">Limitations:</strong>
                <span>{selectedCard.limitations}</span>
              </div>

              <div>
                <strong className="text-white block mb-1">Empirical Evaluation Metrics:</strong>
                <pre className="p-3 rounded-lg bg-dark-900 text-slate-200 font-mono text-[11px] overflow-x-auto">
                  {JSON.stringify(selectedCard.metrics, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
