import React, { useState } from 'react';
import { 
  FlaskConical, 
  Play, 
  CheckCircle2, 
  Layers, 
  Loader2,
  Table as TableIcon
} from 'lucide-react';
import { api } from '../services/api';

export const Experiments: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [sampleLimit, setSampleLimit] = useState(250);
  const [ablationResults, setAblationResults] = useState<any[] | null>(null);

  const handleRunAblation = async () => {
    setIsRunning(true);
    try {
      const res = await api.runAblation(sampleLimit);
      setAblationResults(res.results);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <FlaskConical className="w-7 h-7 text-brand-400" />
          <span>Multimodal Ablation Studies</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Empirically evaluate individual modality contributions (Text-only vs. Text+Stylometry vs. Full VeritasFusion).
        </p>
      </div>

      {/* Trigger Box */}
      <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 flex flex-col sm:flex-row items-end justify-between gap-4">
        <div className="space-y-1">
          <label className="text-xs font-semibold text-slate-300">Ablation Evaluation Subsample Size</label>
          <input
            type="number"
            value={sampleLimit}
            onChange={(e) => setSampleLimit(Number(e.target.value))}
            className="w-48 px-3.5 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100 text-xs font-mono"
          />
          <span className="text-[11px] text-slate-500 block">CPU safe sample range: 100 - 500 samples</span>
        </div>

        <button
          onClick={handleRunAblation}
          disabled={isRunning}
          className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs flex items-center space-x-2 disabled:opacity-50 transition-colors shadow-md"
        >
          {isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          <span>{isRunning ? 'Running Multi-Condition Ablation...' : 'Execute Empirical Ablation Suite'}</span>
        </button>
      </div>

      {/* Results Comparison Table */}
      {ablationResults && (
        <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
              <TableIcon className="w-4 h-4 text-brand-400" />
              <span>Ablation Comparison Matrix (Empirical Findings)</span>
            </h3>
            <span className="text-xs text-slate-400 font-mono">Evaluated on CPU</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-dark-900 text-slate-400 font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4 rounded-l-lg">Architecture / Modality Configuration</th>
                  <th className="py-3 px-4">Active Modalities</th>
                  <th className="py-3 px-4 font-bold text-slate-200">Macro F1</th>
                  <th className="py-3 px-4">Accuracy</th>
                  <th className="py-3 px-4 rounded-r-lg">Scientific Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {ablationResults.map((row, idx) => (
                  <tr key={idx} className="hover:bg-dark-900/60 transition-colors">
                    <td className="py-3 px-4 font-semibold text-white">
                      {row.configuration}
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      <div className="flex flex-wrap gap-1">
                        {row.modalities?.map((m: string, i: number) => (
                          <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                            {m}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-brand-300 text-sm">
                      {row.macro_f1}
                    </td>
                    <td className="py-3 px-4 font-mono text-emerald-400">
                      {row.accuracy}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">
                      {row.notes}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
