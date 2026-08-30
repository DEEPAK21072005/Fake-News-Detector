import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  FileQuestion, 
  ShieldAlert, 
  Clock, 
  Gauge, 
  Sparkles,
  Info
} from 'lucide-react';
import { AnalysisResponse, VerdictType } from '../types';

interface VerdictCardProps {
  analysis: AnalysisResponse;
}

export const VerdictCard: React.FC<VerdictCardProps> = ({ analysis }) => {
  const getVerdictConfig = (verdict: VerdictType) => {
    switch (verdict) {
      case 'LIKELY_REAL':
        return {
          title: 'Likely Real',
          subtitle: 'Content exhibits credible journalistic patterns and corroborating factual support.',
          bgColor: 'bg-emerald-950/40 border-emerald-500/40',
          textColor: 'text-emerald-400',
          badgeBg: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
          icon: CheckCircle2,
          glowColor: 'shadow-emerald-500/10',
        };
      case 'LIKELY_FAKE':
        return {
          title: 'Likely Fake',
          subtitle: 'Content exhibits deceptive stylometric signals or conflicts with verified reporting.',
          bgColor: 'bg-rose-950/40 border-rose-500/40',
          textColor: 'text-rose-400',
          badgeBg: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
          icon: ShieldAlert,
          glowColor: 'shadow-rose-500/10',
        };
      case 'UNCERTAIN':
        return {
          title: 'Uncertain / Conflicted',
          subtitle: 'Mixed stylistic signals and inconclusive retrieval evidence prevent definitive classification.',
          bgColor: 'bg-amber-950/40 border-amber-500/40',
          textColor: 'text-amber-400',
          badgeBg: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
          icon: AlertTriangle,
          glowColor: 'shadow-amber-500/10',
        };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return {
          title: 'Insufficient Evidence',
          subtitle: 'Minimal evidence available in the verification index for this specific assertion.',
          bgColor: 'bg-slate-900/60 border-slate-700',
          textColor: 'text-slate-300',
          badgeBg: 'bg-slate-800 text-slate-300 border-slate-700',
          icon: FileQuestion,
          glowColor: 'shadow-slate-500/10',
        };
    }
  };

  const config = getVerdictConfig(analysis.verdict);
  const Icon = config.icon;
  const confidencePct = Math.round(analysis.calibrated_confidence * 100);

  return (
    <div className={`rounded-2xl p-6 sm:p-8 border ${config.bgColor} shadow-xl ${config.glowColor} relative overflow-hidden`}>
      {/* Background Accent Gradient */}
      <div className="absolute top-0 right-0 -mt-8 -mr-8 w-48 h-48 rounded-full bg-brand-500/5 blur-3xl pointer-events-none"></div>

      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        {/* Left: Main Verdict Header */}
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className={`p-2.5 rounded-xl border ${config.badgeBg}`}>
              <Icon className={`w-8 h-8 ${config.textColor}`} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${config.textColor}`}>
                  {config.title}
                </h2>
                <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${config.badgeBg}`}>
                  {confidencePct}% Calibrated Confidence
                </span>
              </div>
              <p className="text-sm text-slate-300 mt-0.5 max-w-xl">{config.subtitle}</p>
            </div>
          </div>
        </div>

        {/* Right: Key Metric Gauges */}
        <div className="grid grid-cols-3 gap-3 sm:gap-4 bg-dark-900/80 p-4 rounded-xl border border-slate-800/80">
          <div className="text-center px-2">
            <div className="flex items-center justify-center space-x-1 text-slate-400 text-xs mb-1">
              <Gauge className="w-3.5 h-3.5" />
              <span>Evidence</span>
            </div>
            <div className={`text-sm sm:text-base font-bold ${
              analysis.evidence_strength === 'Strong' ? 'text-emerald-400' :
              analysis.evidence_strength === 'Moderate' ? 'text-indigo-300' : 'text-slate-400'
            }`}>
              {analysis.evidence_strength}
            </div>
          </div>

          <div className="text-center px-2 border-x border-slate-800">
            <div className="flex items-center justify-center space-x-1 text-slate-400 text-xs mb-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Reliability</span>
            </div>
            <div className={`text-sm sm:text-base font-bold ${
              analysis.reliability === 'High' ? 'text-emerald-400' :
              analysis.reliability === 'Moderate' ? 'text-amber-400' : 'text-rose-400'
            }`}>
              {analysis.reliability}
            </div>
          </div>

          <div className="text-center px-2">
            <div className="flex items-center justify-center space-x-1 text-slate-400 text-xs mb-1">
              <Clock className="w-3.5 h-3.5" />
              <span>Latency</span>
            </div>
            <div className="text-sm sm:text-base font-bold font-mono text-slate-200">
              {Math.round(analysis.latency_ms)}ms
            </div>
          </div>
        </div>
      </div>

      {/* Rationale Bullet Points */}
      {analysis.key_reasons && analysis.key_reasons.length > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-800/80">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-1.5">
            <Info className="w-3.5 h-3.5 text-brand-400" />
            <span>Primary Verification Factors</span>
          </h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs sm:text-sm text-slate-300">
            {analysis.key_reasons.map((reason, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-brand-400 font-bold mt-0.5">•</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
