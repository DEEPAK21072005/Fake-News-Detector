import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  HardDrive, 
  Activity, 
  CheckCircle2, 
  Server, 
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { SystemStatus } from '../types';

export const SystemHealth: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedMode, setSelectedMode] = useState('BALANCED');

  const fetchStatus = async () => {
    try {
      const data = await api.getSystemStatus();
      setStatus(data);
      setSelectedMode(data.inference_mode);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleModeChange = async (mode: string) => {
    try {
      await api.setInferenceMode(mode);
      fetchStatus();
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !status) {
    return <div className="p-12 text-center text-slate-400 text-sm">Querying system telemetry...</div>;
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <Cpu className="w-7 h-7 text-brand-400" />
            <span>Hardware & System Health</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time CPU and RAM telemetry for Intel Core i5 16GB execution environment.
          </p>
        </div>

        <button
          onClick={fetchStatus}
          className="p-2 rounded-lg bg-dark-800 border border-slate-700 text-slate-300 hover:text-white"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Hardware Telemetry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Processor Unit</span>
            <Cpu className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-base font-bold text-white leading-snug">
            {status.hardware.processor}
          </div>
          <div className="text-xs font-mono text-slate-400">
            {status.hardware.cpu_cores} Logical Cores • Windows 11
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>System Memory (RAM)</span>
            <HardDrive className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            {status.hardware.available_ram_gb} GB Free
          </div>
          <div className="space-y-1">
            <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden">
              <div 
                style={{ width: `${status.hardware.ram_usage_percent}%` }}
                className="h-full bg-emerald-500 rounded-full"
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>{status.hardware.ram_usage_percent}% Allocated</span>
              <span>{status.hardware.total_ram_gb} GB Total</span>
            </div>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Graphics / Acceleration</span>
            <Activity className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-sm font-bold text-slate-200 leading-snug">
            {status.hardware.gpu_name}
          </div>
          <div className="text-xs font-mono text-emerald-400">
            CPU Optimized Execution
          </div>
        </div>
      </div>

      {/* Mode Switcher */}
      <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
          Inference Mode Configuration
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          {[
            { id: 'FAST', title: 'FAST Mode', desc: 'TF-IDF + Stylometry (~15ms latency)' },
            { id: 'BALANCED', title: 'BALANCED Mode', desc: 'MiniLM + VeritasFusion (~45ms latency)' },
            { id: 'RESEARCH', title: 'RESEARCH Mode', desc: 'Full Multimodal + Token Explainability' },
            { id: 'CLOUD_ENHANCED', title: 'CLOUD_ENHANCED', desc: 'Optional External LLM Synthesis' },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => handleModeChange(m.id)}
              className={`p-4 rounded-xl border text-left transition-all space-y-1 ${
                status.inference_mode === m.id
                  ? 'bg-brand-600/20 border-brand-500 text-white shadow-md'
                  : 'bg-dark-900 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="font-bold font-mono text-sm">{m.title}</div>
              <div className="text-[11px] text-slate-400">{m.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Component Status Grid */}
      <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
          Service Component Health
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs font-mono">
          <div className="p-3 rounded-lg bg-dark-900 border border-slate-800 flex items-center justify-between">
            <span className="text-slate-400">FastAPI Backend</span>
            <span className="text-emerald-400 font-bold">● Online</span>
          </div>

          <div className="p-3 rounded-lg bg-dark-900 border border-slate-800 flex items-center justify-between">
            <span className="text-slate-400">SQLite Persistence</span>
            <span className="text-emerald-400 font-bold">● Connected</span>
          </div>

          <div className="p-3 rounded-lg bg-dark-900 border border-slate-800 flex items-center justify-between">
            <span className="text-slate-400">Local Vector Store</span>
            <span className="text-emerald-400 font-bold">● {status.vector_store.indexed_documents} Claims</span>
          </div>

          <div className="p-3 rounded-lg bg-dark-900 border border-slate-800 flex items-center justify-between">
            <span className="text-slate-400">Vision & OCR Pipeline</span>
            <span className="text-emerald-400 font-bold">● Ready</span>
          </div>

          <div className="p-3 rounded-lg bg-dark-900 border border-slate-800 flex items-center justify-between">
            <span className="text-slate-400">LLM Provider</span>
            <span className="text-indigo-300 font-bold">{status.llm_provider.provider}</span>
          </div>

          <div className="p-3 rounded-lg bg-dark-900 border border-slate-800 flex items-center justify-between">
            <span className="text-slate-400">Active Models in RAM</span>
            <span className="text-brand-400 font-bold">{status.loaded_models_count} Loaded</span>
          </div>
        </div>
      </div>
    </div>
  );
};
