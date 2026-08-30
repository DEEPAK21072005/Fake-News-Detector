import React from 'react';
import { 
  ShieldCheck, 
  Search, 
  Database, 
  Layers, 
  BarChart3, 
  Cpu, 
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { SystemStatus } from '../types';

interface NavbarProps {
  activeView: string;
  setActiveView: (view: string) => void;
  systemStatus: SystemStatus | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeView, setActiveView, systemStatus }) => {
  return (
    <header className="sticky top-0 z-50 bg-[#0B0F19]/90 backdrop-blur-xl border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div 
            className="flex items-center space-x-3 cursor-pointer group"
            onClick={() => setActiveView('verify')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-black tracking-tight text-white font-sans">VeritasAI</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/25">
                  Research Platform
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Multimodal News Verification & Epistemic Reasoning</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              onClick={() => setActiveView('verify')}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeView === 'verify'
                  ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Search className="w-3.5 h-3.5" />
              <span>Verify News</span>
            </button>

            <button
              onClick={() => setActiveView('evidence')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeView === 'evidence'
                  ? 'bg-slate-800 text-white border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Evidence Vault</span>
            </button>

            <button
              onClick={() => setActiveView('models')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeView === 'models'
                  ? 'bg-slate-800 text-white border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Models & Benchmarks</span>
            </button>

            <button
              onClick={() => setActiveView('system')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeView === 'system'
                  ? 'bg-slate-800 text-white border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Cpu className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Telemetry</span>
            </button>
          </nav>

          {/* Status Indicator */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300 font-mono text-[11px]">
                {systemStatus?.inference_mode || 'BALANCED'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
