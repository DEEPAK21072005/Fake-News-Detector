import React from 'react';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  FileText, 
  AlertCircle, 
  Sparkles,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { AnalysisResponse } from '../types';
import { VerdictCard } from '../components/VerdictCard';
import { ClaimList } from '../components/ClaimList';
import { EvidenceList } from '../components/EvidenceList';
import { NarrativePanel } from '../components/NarrativePanel';
import { ModalityBreakdown } from '../components/ModalityBreakdown';
import { LinguisticRadar } from '../components/LinguisticRadar';
import { TokenAttributionHighlighter } from '../components/TokenAttributionHighlighter';

interface AnalysisResultsViewProps {
  analysis: AnalysisResponse;
  onBack: () => void;
}

export const AnalysisResultsView: React.FC<AnalysisResultsViewProps> = ({ analysis, onBack }) => {
  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analysis, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `veritas_report_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-white px-3 py-1.5 rounded-lg bg-dark-800 border border-slate-800 hover:border-slate-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Workspace</span>
        </button>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleExportJSON}
            className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-dark-800 border border-slate-800 hover:border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Report (JSON)</span>
          </button>
        </div>
      </div>

      {/* Main Verdict Card */}
      <VerdictCard analysis={analysis} />

      {/* LLM / High-Level Explanation Synthesis Card */}
      {analysis.llm_synthesis && (
        <div className="p-5 rounded-xl bg-gradient-to-r from-brand-950/40 via-dark-800 to-dark-800 border border-brand-500/30 space-y-2">
          <div className="flex items-center space-x-2 text-xs font-bold text-brand-300 uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>AI Verification Synthesis ({analysis.llm_synthesis.provider})</span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed font-sans">
            {analysis.llm_synthesis.summary}
          </p>
        </div>
      )}

      {/* Two Column Grid for Multimodal Breakdown & Linguistic Signals */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ModalityBreakdown breakdown={analysis.modality_breakdown} />
        <LinguisticRadar signals={analysis.linguistic_signals} />
      </div>

      {/* Extracted Claim Assertions */}
      <ClaimList claims={analysis.claims} />

      {/* Verified Retrieval Evidence */}
      <EvidenceList
        supporting={analysis.supporting_evidence}
        contradicting={analysis.contradicting_evidence}
        related={analysis.related_evidence}
      />

      {/* Narrative Consistency Analysis */}
      <NarrativePanel narrative={analysis.narrative_consistency} />

      {/* Explainable Token Attribution Cloud */}
      <TokenAttributionHighlighter attributions={analysis.token_attributions} />

      {/* Research Limitations & Ethical Disclaimers */}
      <div className="p-5 rounded-xl bg-dark-900/90 border border-slate-800 text-xs space-y-2.5">
        <h4 className="font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-amber-400" />
          <span>Research Limitations & Epistemic Disclaimers</span>
        </h4>
        <ul className="space-y-1.5 text-slate-400 text-[11px] leading-relaxed">
          {analysis.limitations.map((lim, idx) => (
            <li key={idx} className="flex items-start space-x-2">
              <span className="text-slate-500">•</span>
              <span>{lim}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
