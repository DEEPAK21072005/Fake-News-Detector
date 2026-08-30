import React from 'react';
import { Activity, Flame, AlertCircle, Type, HeartHandshake } from 'lucide-react';
import { LinguisticSignals } from '../types';

interface LinguisticRadarProps {
  signals: LinguisticSignals;
}

export const LinguisticRadar: React.FC<LinguisticRadarProps> = ({ signals }) => {
  const metrics = [
    {
      label: 'Sensationalism',
      val: Math.round((signals.sensationalism_score || 0) * 100),
      color: 'bg-rose-500',
      icon: Flame,
      desc: 'Emotional triggers & hyperbole',
    },
    {
      label: 'Clickbait Index',
      val: Math.round((signals.clickbait_score || 0) * 100),
      color: 'bg-amber-500',
      icon: AlertCircle,
      desc: 'Headline structure & exaggerated curiosity',
    },
    {
      label: 'Uppercase Density',
      val: Math.round((signals.uppercase_ratio || 0) * 100),
      color: 'bg-indigo-500',
      icon: Type,
      desc: 'ALL-CAPS word frequency',
    },
    {
      label: 'Emotional Intensity',
      val: Math.round((signals.emotional_intensity || 0) * 100),
      color: 'bg-purple-500',
      icon: HeartHandshake,
      desc: 'Affect-bearing token concentration',
    },
  ];

  return (
    <div className="bg-dark-800/90 rounded-xl p-5 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
          <Activity className="w-4 h-4 text-brand-400" />
          <span>Linguistic & Stylometric Signals</span>
        </h3>
        <span className="text-xs text-slate-500 font-mono">
          {signals.total_words} Words / {signals.total_sentences} Sentences
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {metrics.map((m) => {
          const Icon = m.icon;
          return (
            <div key={m.label} className="p-3 rounded-lg bg-dark-900/80 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-semibold flex items-center space-x-1.5">
                  <Icon className="w-3.5 h-3.5 text-slate-400" />
                  <span>{m.label}</span>
                </span>
                <span className="font-mono font-bold text-slate-200">{m.val}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div 
                  style={{ width: `${Math.min(100, m.val)}%` }} 
                  className={`h-full ${m.color} transition-all duration-500`}
                />
              </div>
              <p className="text-[10px] text-slate-500 truncate">{m.desc}</p>
            </div>
          );
        })}
      </div>

      {signals.sensational_keywords_found && signals.sensational_keywords_found.length > 0 && (
        <div className="pt-2 border-t border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-1.5">Detected Trigger Phrases:</span>
          <div className="flex flex-wrap gap-1.5">
            {signals.sensational_keywords_found.map((kw, i) => (
              <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 font-mono">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
