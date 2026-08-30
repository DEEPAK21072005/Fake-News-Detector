import React, { useState } from 'react';
import { Settings as SettingsIcon, Key, Sliders, Shield, Save, CheckCircle2 } from 'lucide-react';

export const Settings: React.FC = () => {
  const [llmProvider, setLlmProvider] = useState('null');
  const [apiKey, setApiKey] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <SettingsIcon className="w-7 h-7 text-brand-400" />
          <span>Platform Settings & API Keys</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure optional cloud reasoning providers, classification thresholds, and privacy preferences.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Optional Cloud LLM Section */}
        <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <Key className="w-4 h-4 text-brand-400" />
            <span>Optional External LLM Synthesis</span>
          </h3>
          <p className="text-xs text-slate-400">
            VeritasAI operates 100% offline by default with NullProvider. You may optionally configure a cloud LLM for high-level narrative explanation synthesis.
          </p>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-300 mb-1 font-semibold">LLM Provider</label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
              >
                <option value="null">NullProvider (100% Offline Local Synthesis - Default)</option>
                <option value="gemini">Google Gemini (gemini-2.5-flash)</option>
                <option value="openai">OpenAI / OpenAI-Compatible (Local vLLM / Ollama)</option>
              </select>
            </div>

            {llmProvider !== 'null' && (
              <div>
                <label className="block text-slate-300 mb-1 font-semibold">API Secret Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter API Key..."
                  className="w-full px-3.5 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100 font-mono"
                />
              </div>
            )}
          </div>
        </div>

        {/* Epistemic Privacy Section */}
        <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-3 text-xs">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <Shield className="w-4 h-4 text-brand-400" />
            <span>Data Privacy & Zero-Retention Policy</span>
          </h3>
          <p className="text-slate-300 leading-relaxed">
            All text embeddings, visual descriptors, and claim extractions are processed locally on your Intel CPU. 
            No article text or uploaded images are transmitted to external servers unless an explicit cloud LLM provider is configured.
          </p>
        </div>

        {/* Save Button */}
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs flex items-center space-x-2 shadow-md"
          >
            <Save className="w-4 h-4" />
            <span>Save Preferences</span>
          </button>

          {saved && (
            <span className="text-xs text-emerald-400 font-mono flex items-center space-x-1">
              <CheckCircle2 className="w-4 h-4" />
              <span>Settings updated successfully.</span>
            </span>
          )}
        </div>
      </form>
    </div>
  );
};
