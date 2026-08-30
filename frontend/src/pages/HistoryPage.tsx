import React, { useEffect, useState } from 'react';
import {
  History, ShieldAlert, ShieldCheck, AlertTriangle, FileQuestion,
  Clock, ChevronRight, RefreshCw, Calendar, Loader2
} from 'lucide-react';
import { api } from '../services/api';
import { AnalysisResponse, VerdictType } from '../types';

const VERDICT_BADGE: Record<VerdictType, { label: string; cls: string }> = {
  LIKELY_REAL: { label: '✅ Likely Real', cls: 'bg-neon-green/10 text-neon-green border-neon-green/25' },
  LIKELY_FAKE: { label: '🚨 Likely Fake', cls: 'bg-neon-red/10 text-neon-red border-neon-red/25' },
  UNCERTAIN: { label: '⚠️ Uncertain', cls: 'bg-neon-amber/10 text-neon-amber border-neon-amber/25' },
  INSUFFICIENT_EVIDENCE: { label: '❓ Insufficient', cls: 'bg-slate-700/50 text-slate-300 border-slate-600/30' },
};

const HistoryCard: React.FC<{ item: AnalysisResponse; idx: number }> = ({ item, idx }) => {
  const badge = VERDICT_BADGE[item.verdict] ?? VERDICT_BADGE.INSUFFICIENT_EVIDENCE;
  const conf = Math.round(item.calibrated_confidence * 100);

  return (
    <div
      className="glass-card rounded-xl p-4 hover-lift transition-all animate-fade-up cursor-default"
      style={{ animationDelay: `${idx * 0.06}s`, opacity: 0 }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0 space-y-1.5">
          {/* Title */}
          <p className="text-sm font-semibold text-slate-100 line-clamp-2 leading-snug">
            {item.title || item.content_preview?.slice(0, 120) || 'Untitled analysis'}
          </p>

          {/* Meta row */}
          <div className="flex items-center flex-wrap gap-x-3 gap-y-1 text-[10px] text-slate-500">
            {item.created_at && (
              <span className="flex items-center space-x-1">
                <Calendar className="w-2.5 h-2.5" />
                <span>{new Date(item.created_at).toLocaleDateString('en-IN', {
                  day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
                })}</span>
              </span>
            )}
            <span className="flex items-center space-x-1">
              <Clock className="w-2.5 h-2.5" />
              <span className="font-mono">{Math.round(item.latency_ms)}ms</span>
            </span>
            <span className="font-mono">{item.inference_mode}</span>
            {item.source_url && (
              <span className="text-brand-500/60 truncate max-w-[140px]">{item.source_url}</span>
            )}
          </div>
        </div>

        {/* Right: badges */}
        <div className="flex flex-col items-end space-y-2 flex-shrink-0">
          <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${badge.cls}`}>
            {badge.label}
          </span>
          <span className="text-xs font-black font-display text-slate-300">
            {conf}%
          </span>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="mt-3 h-0.5 bg-white/[0.04] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${conf}%`,
            background: item.verdict === 'LIKELY_REAL' ? '#34D399' :
                        item.verdict === 'LIKELY_FAKE' ? '#F87171' :
                        item.verdict === 'UNCERTAIN' ? '#FCD34D' : '#6B7280'
          }}
        />
      </div>
    </div>
  );
};

export const HistoryPage: React.FC = () => {
  const [items, setItems] = useState<AnalysisResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHistory(20);
      setItems(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load history.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!window.confirm('Are you sure you want to clear all verification history?')) return;
    try {
      await api.clearHistory();
      setItems([]);
    } catch (e: any) {
      setError(e.message || 'Failed to clear history.');
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center">
            <History className="w-5 h-5 text-brand-400" />
          </div>
          <div>
            <h1 className="text-xl font-black font-display text-white">Verification History</h1>
            <p className="text-xs text-slate-500">Past analyses stored locally</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {items.length > 0 && (
            <button
              onClick={handleClear}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-neon-red/10 border border-neon-red/20 text-xs font-semibold text-neon-red hover:bg-neon-red/20 transition-all"
            >
              <span>Clear History</span>
            </button>
          )}

          <button
            onClick={load}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl glass border border-white/[0.06] text-xs font-semibold text-slate-300 hover:text-white transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* States */}
      {loading && (
        <div className="flex items-center justify-center py-20 text-slate-500">
          <Loader2 className="w-6 h-6 animate-spin mr-3" />
          <span className="text-sm">Loading history...</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-neon-red/10 border border-neon-red/25 text-neon-red text-sm text-center">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="text-center py-20 space-y-3">
          <div className="w-16 h-16 rounded-2xl glass mx-auto flex items-center justify-center mb-4">
            <History className="w-8 h-8 text-slate-600" />
          </div>
          <p className="text-slate-400 font-semibold">No verifications yet</p>
          <p className="text-slate-600 text-sm">Run your first analysis to see history here</p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <>
          {/* Stats bar */}
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: 'Total', value: items.length, color: 'text-slate-200' },
              { label: 'Likely Fake', value: items.filter(i => i.verdict === 'LIKELY_FAKE').length, color: 'text-neon-red' },
              { label: 'Likely Real', value: items.filter(i => i.verdict === 'LIKELY_REAL').length, color: 'text-neon-green' },
              { label: 'Uncertain', value: items.filter(i => i.verdict === 'UNCERTAIN').length, color: 'text-neon-amber' },
            ].map(s => (
              <div key={s.label} className="glass-card rounded-xl p-3 text-center">
                <p className={`text-2xl font-black font-display ${s.color}`}>{s.value}</p>
                <p className="text-[9px] font-mono uppercase tracking-widest text-slate-600 mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>

          {/* Cards */}
          <div className="space-y-3">
            {items.map((item, i) => (
              <HistoryCard key={item.id ?? i} item={item} idx={i} />
            ))}
          </div>
        </>
      )}
    </div>
  );
};
