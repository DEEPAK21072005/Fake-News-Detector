import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  Globe, 
  Award,
  Link2
} from 'lucide-react';
import { EvidenceItem } from '../types';

interface EvidenceListProps {
  supporting: EvidenceItem[];
  contradicting: EvidenceItem[];
  related: EvidenceItem[];
}

export const EvidenceList: React.FC<EvidenceListProps> = ({ supporting, contradicting, related }) => {
  const [filter, setFilter] = useState<'all' | 'contradicting' | 'supporting' | 'related'>('all');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const allEvidence = [
    ...contradicting.map(e => ({ ...e, group: 'contradicting' })),
    ...supporting.map(e => ({ ...e, group: 'supporting' })),
    ...related.map(e => ({ ...e, group: 'related' })),
  ];

  const filteredItems = allEvidence.filter(item => {
    if (filter === 'all') return true;
    return item.group === filter;
  });

  const getStanceBadge = (stance: string) => {
    const s = stance.toLowerCase();
    if (s.includes('contradict') || s.includes('debunk') || s.includes('fake')) {
      return {
        bg: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
        icon: ShieldAlert,
        label: 'Contradicts Claim',
      };
    }
    if (s.includes('support') || s.includes('confirm') || s.includes('true')) {
      return {
        bg: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
        icon: ShieldCheck,
        label: 'Supports Claim',
      };
    }
    return {
      bg: 'bg-slate-700 text-slate-300 border-slate-600',
      icon: Globe,
      label: 'Contextual Reporting',
    };
  };

  return (
    <div className="bg-dark-800/90 rounded-xl p-5 border border-slate-800 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-brand-400" />
            <span>Retrieved Verified Evidence ({allEvidence.length})</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Vector similarity matching & domain authority weighting</p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center space-x-1 bg-dark-900 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setFilter('all')}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${filter === 'all' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            All ({allEvidence.length})
          </button>
          <button
            onClick={() => setFilter('contradicting')}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${filter === 'contradicting' ? 'bg-rose-600 text-white' : 'text-rose-400 hover:text-rose-200'}`}
          >
            Contradicting ({contradicting.length})
          </button>
          <button
            onClick={() => setFilter('supporting')}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${filter === 'supporting' ? 'bg-emerald-600 text-white' : 'text-emerald-400 hover:text-emerald-200'}`}
          >
            Supporting ({supporting.length})
          </button>
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <div className="p-8 text-center bg-dark-900/50 rounded-lg border border-slate-800 text-slate-400 text-xs">
          No matching evidence records found in the current filter category.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredItems.map((item, idx) => {
            const badge = getStanceBadge(item.stance);
            const StanceIcon = badge.icon;
            const isExpanded = expandedId === (item.id || idx);

            return (
              <div
                key={item.id || idx}
                className="p-4 rounded-lg bg-dark-900/90 border border-slate-800 hover:border-slate-700 transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border flex items-center space-x-1 ${badge.bg}`}>
                        <StanceIcon className="w-3 h-3" />
                        <span>{badge.label}</span>
                      </span>

                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 flex items-center space-x-1">
                        <Award className="w-3 h-3 text-amber-400" />
                        <span>{Math.round(item.credibility_score * 100)}% Source Authority</span>
                      </span>

                      <span className="text-[10px] font-mono text-slate-400">
                        {Math.round(item.similarity * 100)}% Cosine Match
                      </span>
                    </div>

                    <h4 className="text-sm font-semibold text-slate-100 leading-snug">
                      {item.title}
                    </h4>

                    <p className={`text-xs text-slate-300 leading-relaxed ${isExpanded ? '' : 'line-clamp-2'}`}>
                      {item.text}
                    </p>

                    <div className="flex items-center space-x-4 pt-1 text-[11px] text-slate-400">
                      <span>Source: <strong className="text-slate-200">{item.source}</strong></span>
                      {item.publication_date && <span>Date: {item.publication_date}</span>}
                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-brand-400 hover:underline flex items-center space-x-1"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span>View Original</span>
                        </a>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => setExpandedId(isExpanded ? null : (item.id || idx))}
                    className="p-1.5 rounded hover:bg-slate-800 text-slate-400"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
