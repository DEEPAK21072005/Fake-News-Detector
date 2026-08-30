import React from 'react';
import { Target, CheckCircle, AlertCircle } from 'lucide-react';
import { ClaimItem } from '../types';

interface ClaimListProps {
  claims: ClaimItem[];
}

export const ClaimList: React.FC<ClaimListProps> = ({ claims }) => {
  if (!claims || claims.length === 0) return null;

  return (
    <div className="bg-dark-800/90 rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
          <Target className="w-4 h-4 text-brand-400" />
          <span>Extracted Factual Propositions ({claims.length})</span>
        </h3>
        <span className="text-xs text-slate-500 font-mono">Syntactic Claim Decomposition</span>
      </div>

      <div className="space-y-3">
        {claims.map((claim) => (
          <div 
            key={claim.claim_id}
            className="p-3.5 rounded-lg bg-dark-900/90 border border-slate-800/80 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1 flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
                    {claim.type}
                  </span>
                  {claim.is_title_claim && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                      Primary Headline
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-200 font-medium leading-relaxed">
                  "{claim.text}"
                </p>
              </div>

              <div className="text-right">
                <span className="text-xs text-slate-400 font-mono">
                  {Math.round(claim.confidence * 100)}% Extraction Conf
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
