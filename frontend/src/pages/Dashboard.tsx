import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  HelpCircle, 
  FileCheck2, 
  TrendingUp, 
  Zap, 
  Layers, 
  ArrowRight,
  Database,
  Cpu
} from 'lucide-react';
import { api } from '../services/api';
import { AnalysisResponse, SystemStatus } from '../types';

interface DashboardProps {
  onNavigate: (tab: string, item?: any) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [history, setHistory] = useState<AnalysisResponse[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [hist, sys] = await Promise.all([
          api.getHistory(10),
          api.getSystemStatus(),
        ]);
        setHistory(hist);
        setSystemStatus(sys);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const total = history.length;
  const fakeCount = history.filter(h => h.verdict === 'LIKELY_FAKE').length;
  const realCount = history.filter(h => h.verdict === 'LIKELY_REAL').length;
  const uncertainCount = history.filter(h => h.verdict === 'UNCERTAIN' || h.verdict === 'INSUFFICIENT_EVIDENCE').length;
  const avgConfidence = total > 0 
    ? Math.round(history.reduce((acc, curr) => acc + curr.calibrated_confidence, 0) / total * 100) 
    : 85;

  return (
    <div className="space-y-8">
      {/* Top Banner / Hero Section */}
      <div className="rounded-2xl p-6 sm:p-8 bg-gradient-to-r from-dark-800 via-dark-800 to-brand-950/40 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-brand-400 text-xs font-bold uppercase tracking-wider">
            <Zap className="w-4 h-4" />
            <span>Research-Grade Epistemic Verification</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            VeritasAI Verification Dashboard
          </h1>
          <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
            Multimodal detection platform decoupling stylistic deception classification from 
            retrieval-augmented evidence verification and cross-instance narrative consistency.
          </p>
        </div>

        <button
          onClick={() => onNavigate('analyze')}
          className="px-5 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm shadow-lg shadow-brand-500/25 flex items-center space-x-2 transition-all transform hover:-translate-y-0.5 whitespace-nowrap"
        >
          <span>Start New Analysis</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="p-5 rounded-xl bg-dark-800/90 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Analyses</span>
            <FileCheck2 className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold font-mono text-white">
            {total}
          </div>
          <div className="text-[11px] text-slate-400">Indexed Verification Sessions</div>
        </div>

        <div className="p-5 rounded-xl bg-dark-800/90 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Likely Fake Detected</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold font-mono text-rose-400">
            {fakeCount}
          </div>
          <div className="text-[11px] text-slate-400">{total > 0 ? Math.round(fakeCount/total*100) : 0}% of evaluated samples</div>
        </div>

        <div className="p-5 rounded-xl bg-dark-800/90 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Likely Real Corroborated</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold font-mono text-emerald-400">
            {realCount}
          </div>
          <div className="text-[11px] text-slate-400">{total > 0 ? Math.round(realCount/total*100) : 0}% of evaluated samples</div>
        </div>

        <div className="p-5 rounded-xl bg-dark-800/90 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Avg. Calibrated Conf</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold font-mono text-amber-400">
            {avgConfidence}%
          </div>
          <div className="text-[11px] text-slate-400">Platt Scaled Probability</div>
        </div>
      </div>

      {/* Two Column Layout: Recent Analyses & System Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Recent Analyses Table */}
        <div className="lg:col-span-2 bg-dark-800/90 rounded-xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Layers className="w-4 h-4 text-brand-400" />
              <span>Recent Verification Reports</span>
            </h3>
            <button
              onClick={() => onNavigate('analyze')}
              className="text-xs text-brand-400 hover:text-brand-300 font-semibold"
            >
              Analyze More →
            </button>
          </div>

          {history.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-sm space-y-3">
              <p>No verification history recorded yet.</p>
              <button
                onClick={() => onNavigate('analyze')}
                className="px-4 py-2 rounded-lg bg-slate-800 text-slate-200 text-xs font-semibold hover:bg-slate-700"
              >
                Analyze a News Article
              </button>
            </div>
          ) : (
            <div className="space-y-2.5">
              {history.map((item) => (
                <div
                  key={item.id || item.created_at}
                  onClick={() => onNavigate('results', item)}
                  className="p-3.5 rounded-lg bg-dark-900/80 border border-slate-800/80 hover:border-slate-700 hover:bg-dark-900 transition-all cursor-pointer flex items-center justify-between gap-4"
                >
                  <div className="space-y-1 flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${
                        item.verdict === 'LIKELY_REAL' ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' :
                        item.verdict === 'LIKELY_FAKE' ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' :
                        'bg-amber-500/10 text-amber-300 border-amber-500/30'
                      }`}>
                        {item.verdict.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        {Math.round(item.calibrated_confidence * 100)}% Conf
                      </span>
                      <span className="text-[11px] text-slate-500">
                        • {item.evidence_strength} Evidence
                      </span>
                    </div>
                    <h4 className="text-sm font-medium text-slate-200 truncate">
                      {item.title || item.content_preview}
                    </h4>
                  </div>

                  <ArrowRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Hardware & Architecture Status */}
        <div className="bg-dark-800/90 rounded-xl p-6 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-brand-400" />
            <span>Platform Telemetry</span>
          </h3>

          {systemStatus && (
            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-dark-900/80 border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase">Processor & Architecture</span>
                <div className="font-semibold text-slate-200">{systemStatus.hardware.processor}</div>
                <div className="text-slate-400 font-mono">{systemStatus.hardware.cpu_cores} Cores • CPU Inference</div>
              </div>

              <div className="p-3 rounded-lg bg-dark-900/80 border border-slate-800 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase">RAM Allocation & Safety</span>
                <div className="flex justify-between font-mono text-slate-200">
                  <span>Usage: {systemStatus.hardware.ram_usage_percent}%</span>
                  <span>{systemStatus.hardware.available_ram_gb} GB Free / {systemStatus.hardware.total_ram_gb} GB</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden mt-1">
                  <div 
                    style={{ width: `${systemStatus.hardware.ram_usage_percent}%` }}
                    className="h-full bg-brand-500 rounded-full"
                  />
                </div>
              </div>

              <div className="p-3 rounded-lg bg-dark-900/80 border border-slate-800 space-y-1.5 font-mono text-[11px]">
                <div className="flex justify-between">
                  <span className="text-slate-400">Vector Store:</span>
                  <span className="text-emerald-400 font-semibold">{systemStatus.vector_store.indexed_documents} Indexed Claims</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Active Model:</span>
                  <span className="text-brand-300 font-semibold">VeritasFusion Engine</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Inference Mode:</span>
                  <span className="text-indigo-400 font-semibold">{systemStatus.inference_mode}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
