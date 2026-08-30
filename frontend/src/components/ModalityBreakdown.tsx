import React from 'react';
import { Layers, FileText, Image as ImageIcon, Database } from 'lucide-react';
import { ModalityBreakdown as ModalityType } from '../types';

interface ModalityBreakdownProps {
  breakdown: ModalityType;
}

export const ModalityBreakdown: React.FC<ModalityBreakdownProps> = ({ breakdown }) => {
  const textPct = Math.round(breakdown.text_percentage || 0);
  const imgPct = Math.round(breakdown.image_percentage || 0);
  const evPct = Math.round(breakdown.evidence_percentage || 0);

  return (
    <div className="bg-dark-800/90 rounded-xl p-5 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
          <Layers className="w-4 h-4 text-brand-400" />
          <span>Multimodal Decision Contribution</span>
        </h3>
        <span className="text-xs text-slate-500 font-mono">Cross-Modal Gating %</span>
      </div>

      {/* Stacked Bar */}
      <div className="h-3 w-full bg-dark-900 rounded-full overflow-hidden flex border border-slate-800">
        <div 
          style={{ width: `${textPct}%` }} 
          className="bg-indigo-500 transition-all duration-500" 
          title={`Text: ${textPct}%`}
        />
        <div 
          style={{ width: `${imgPct}%` }} 
          className="bg-purple-500 transition-all duration-500" 
          title={`Vision: ${imgPct}%`}
        />
        <div 
          style={{ width: `${evPct}%` }} 
          className="bg-teal-500 transition-all duration-500" 
          title={`Evidence: ${evPct}%`}
        />
      </div>

      {/* Grid of percentages */}
      <div className="grid grid-cols-3 gap-2 pt-1 text-xs">
        <div className="p-2 rounded bg-dark-900/60 border border-slate-800/80 flex items-center space-x-2">
          <FileText className="w-4 h-4 text-indigo-400" />
          <div>
            <div className="text-slate-400 text-[10px]">Text Signals</div>
            <div className="font-bold font-mono text-indigo-300">{textPct}%</div>
          </div>
        </div>

        <div className="p-2 rounded bg-dark-900/60 border border-slate-800/80 flex items-center space-x-2">
          <ImageIcon className="w-4 h-4 text-purple-400" />
          <div>
            <div className="text-slate-400 text-[10px]">Image & OCR</div>
            <div className="font-bold font-mono text-purple-300">{imgPct}%</div>
          </div>
        </div>

        <div className="p-2 rounded bg-dark-900/60 border border-slate-800/80 flex items-center space-x-2">
          <Database className="w-4 h-4 text-teal-400" />
          <div>
            <div className="text-slate-400 text-[10px]">Evidence Match</div>
            <div className="font-bold font-mono text-teal-300">{evPct}%</div>
          </div>
        </div>
      </div>
    </div>
  );
};
