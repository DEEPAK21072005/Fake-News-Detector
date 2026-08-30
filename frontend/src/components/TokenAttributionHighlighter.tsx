import React, { useState } from 'react';
import { Sparkles, HelpCircle, Eye } from 'lucide-react';
import { TokenAttribution } from '../types';

interface TokenAttributionHighlighterProps {
  attributions: TokenAttribution[];
}

export const TokenAttributionHighlighter: React.FC<TokenAttributionHighlighterProps> = ({ attributions }) => {
  const [selectedToken, setSelectedToken] = useState<TokenAttribution | null>(null);

  if (!attributions || attributions.length === 0) return null;

  return (
    <div className="bg-dark-800/90 rounded-xl p-5 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-brand-400" />
          <span>Explainable Feature Attribution</span>
        </h3>
        <span className="text-xs text-slate-500 font-mono">Token-Level Influence</span>
      </div>

      <p className="text-xs text-slate-400">
        Click or hover tokens to inspect the exact mathematical contribution score and feature triggers driving the model's prediction:
      </p>

      {/* Token Pill Cloud */}
      <div className="flex flex-wrap gap-2 p-4 rounded-xl bg-dark-900/90 border border-slate-800/80 max-h-48 overflow-y-auto">
        {attributions.map((item, idx) => {
          const isFakeIndicative = item.polarity === 'Fake-indicative';
          const isSelected = selectedToken?.token === item.token;

          return (
            <button
              key={idx}
              onClick={() => setSelectedToken(isSelected ? null : item)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition-all flex items-center space-x-1.5 ${
                isFakeIndicative
                  ? 'bg-rose-950/50 text-rose-300 border border-rose-500/30 hover:bg-rose-900/60'
                  : 'bg-emerald-950/50 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-900/60'
              } ${isSelected ? 'ring-2 ring-brand-400 shadow-md' : ''}`}
            >
              <span>{item.token}</span>
              <span className={`text-[10px] font-bold ${isFakeIndicative ? 'text-rose-400' : 'text-emerald-400'}`}>
                {item.score > 0 ? `+${item.score}` : item.score}
              </span>
            </button>
          );
        })}
      </div>

      {/* Selected Token Detail Inspector */}
      {selectedToken && (
        <div className="p-3.5 rounded-lg bg-slate-900 border border-brand-500/30 text-xs space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="font-bold font-mono text-brand-300 text-sm">
              "{selectedToken.token}"
            </span>
            <span className={`px-2 py-0.5 rounded font-mono text-[10px] ${
              selectedToken.polarity === 'Fake-indicative' ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
            }`}>
              {selectedToken.polarity} ({selectedToken.score > 0 ? `+${selectedToken.score}` : selectedToken.score})
            </span>
          </div>

          <div className="text-slate-300 text-[11px]">
            <strong>Attribution Drivers:</strong> {selectedToken.reasons.join(', ')}
          </div>
        </div>
      )}
    </div>
  );
};
