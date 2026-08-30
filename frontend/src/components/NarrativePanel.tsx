import React from 'react';
import { GitMerge, Sparkles, AlertCircle } from 'lucide-react';
import { NarrativeConsistencyData } from '../types';

interface NarrativePanelProps {
  narrative: NarrativeConsistencyData;
}

export const NarrativePanel: React.FC<NarrativePanelProps> = ({ narrative }) => {
  const pConsistent = Math.round((narrative.consistent_pct || 0) * 100);
  const pContradictory = Math.round((narrative.contradictory_pct || 0) * 100);
  const pNovel = Math.max(0, 100 - (pConsistent + pContradictory));

  return (
    <div className="bg-dark-800/90 rounded-xl p-5 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
            <GitMerge className="w-4 h-4 text-brand-400" />
            <span>Narrative Consistency & Novelty</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Cross-instance semantic clustering against historical reporting</p>
        </div>

        <span className="text-xs px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-slate-300 font-mono">
          {narrative.dominant_narrative}
        </span>
      </div>

      {/* Progress Bar Distribution */}
      <div className="space-y-2">
        <div className="h-3 w-full bg-dark-900 rounded-full overflow-hidden flex border border-slate-800">
          <div 
            style={{ width: `${pConsistent}%` }} 
            className="bg-emerald-500 transition-all duration-500" 
            title={`Consistent: ${pConsistent}%`}
          />
          <div 
            style={{ width: `${pContradictory}%` }} 
            className="bg-rose-500 transition-all duration-500" 
            title={`Contradictory: ${pContradictory}%`}
          />
          <div 
            style={{ width: `${pNovel}%` }} 
            className="bg-slate-500 transition-all duration-500" 
            title={`Novel/Unknown: ${pNovel}%`}
          />
        </div>

        {/* Legend */}
        <div className="grid grid-cols-3 gap-2 text-xs font-mono pt-1">
          <div className="flex items-center space-x-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span>Consistent: {pConsistent}%</span>
          </div>
          <div className="flex items-center space-x-1.5 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span>Contradictory: {pContradictory}%</span>
          </div>
          <div className="flex items-center space-x-1.5 text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-500"></span>
            <span>Novel/Unindexed: {pNovel}%</span>
          </div>
        </div>
      </div>

      {/* Similar Narratives */}
      {narrative.similar_narratives && narrative.similar_narratives.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-slate-800/80">
          <h4 className="text-xs font-semibold text-slate-400">Nearest Narrative Clusters:</h4>
          <div className="space-y-1.5">
            {narrative.similar_narratives.map((sim, i) => (
              <div key={i} className="text-xs p-2 rounded bg-dark-900/60 border border-slate-800 flex items-center justify-between text-slate-300">
                <span className="truncate flex-1 mr-2">{sim.title}</span>
                <span className="font-mono text-[10px] text-brand-400 whitespace-nowrap">
                  {Math.round(sim.similarity * 100)}% Sim
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
