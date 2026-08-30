import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { VerificationStudio } from './pages/VerificationStudio';
import { EvidenceVault } from './pages/EvidenceVault';
import { Models } from './pages/Models';
import { SystemHealth } from './pages/SystemHealth';
import { api } from './services/api';
import { SystemStatus } from './types';

export const App: React.FC = () => {
  const [activeView, setActiveView] = useState<'verify' | 'evidence' | 'models' | 'system'>('verify');
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await api.getSystemStatus();
        setSystemStatus(status);
      } catch (e) {
        console.error('System status query error:', e);
      }
    };
    checkStatus();
  }, []);

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col selection:bg-brand-600 selection:text-white font-sans antialiased">
      {/* Sleek Top Navigation */}
      <Navbar 
        activeView={activeView} 
        setActiveView={(v) => setActiveView(v as any)} 
        systemStatus={systemStatus} 
      />

      {/* Main Workspace Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeView === 'verify' && <VerificationStudio />}
        {activeView === 'evidence' && <EvidenceVault />}
        {activeView === 'models' && <Models />}
        {activeView === 'system' && <SystemHealth />}
      </main>

      {/* Epistemic Research Footer */}
      <footer className="border-t border-slate-900 bg-dark-900/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 space-y-1">
          <p className="font-bold text-slate-400">VeritasAI: Multimodal Fake News Detection & Verification Platform</p>
          <p className="text-[11px] text-slate-600">
            Engineered for research reproducibility • Intel Core i5 CPU Optimized • Epistemic Decision Support
          </p>
        </div>
      </footer>
    </div>
  );
};
