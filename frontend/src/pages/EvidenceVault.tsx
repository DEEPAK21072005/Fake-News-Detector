import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Search, 
  Plus, 
  ExternalLink, 
  Globe, 
  Award, 
  Database,
  Filter,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { EvidenceItem } from '../types';

export const EvidenceVault: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [category, setCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New Evidence Form State
  const [newTitle, setNewTitle] = useState('');
  const [newText, setNewText] = useState('');
  const [newSource, setNewSource] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [newCategory, setNewCategory] = useState('General');
  const [newStance, setNewStance] = useState('Supporting');

  const fetchEvidence = async () => {
    setLoading(true);
    try {
      const data = await api.listEvidence(category);
      setEvidenceList(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [category]);

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetch('/api/evidence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          text: newText,
          source: newSource,
          url: newUrl,
          category: newCategory,
          stance_tag: newStance
        })
      });
      setShowAddModal(false);
      setNewTitle('');
      setNewText('');
      setNewSource('');
      setNewUrl('');
      fetchEvidence();
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = evidenceList.filter(item => {
    if (!searchQuery) return true;
    return item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
           item.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
           item.source.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <ShieldCheck className="w-7 h-7 text-brand-400" />
            <span>Verified Evidence Vault</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Local vector database with {evidenceList.length} indexed factual and debunked assertions.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md flex items-center space-x-1.5 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Verified Fact</span>
          </button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl bg-dark-800/90 border border-slate-800 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search indexed claims, keywords, or news sources..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
          >
            <option value="All">All Categories</option>
            <option value="Health">Health & Medicine</option>
            <option value="Politics">Politics</option>
            <option value="Science">Science & Climate</option>
            <option value="Economy">Economy</option>
            <option value="World">World News</option>
          </select>
        </div>
      </div>

      {/* Evidence Cards Grid */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          Loading verified evidence index...
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center bg-dark-800/50 rounded-xl border border-slate-800 text-slate-400 text-xs">
          No evidence records found matching your query.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((item, idx) => (
            <div key={item.id || idx} className="p-5 rounded-xl bg-dark-800/90 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full border ${
                  item.stance.toLowerCase().includes('contra') || item.stance.toLowerCase().includes('debunk')
                    ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                    : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                }`}>
                  {item.stance}
                </span>

                <span className="text-[10px] font-mono text-slate-400">
                  {item.category} • {Math.round(item.credibility_score * 100)}% Authority
                </span>
              </div>

              <h4 className="text-sm font-semibold text-slate-100 leading-snug">
                {item.title}
              </h4>

              <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                {item.text}
              </p>

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                <span>Source: <strong className="text-slate-200">{item.source}</strong></span>
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-brand-400 hover:underline flex items-center space-x-1"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span>Reference</span>
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Evidence Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-dark-800 border border-slate-700 rounded-2xl p-6 max-w-lg w-full space-y-4">
            <h3 className="text-base font-bold text-white">Add Verified Claim to Evidence Index</h3>
            
            <form onSubmit={handleAddEvidence} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 mb-1">Claim Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Clinical trials demonstrate..."
                  className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Evidence Text Body</label>
                <textarea
                  rows={3}
                  required
                  value={newText}
                  onChange={(e) => setNewText(e.target.value)}
                  placeholder="Official statement, study findings, or debunking summary..."
                  className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 mb-1">Source / Journal</label>
                  <input
                    type="text"
                    required
                    value={newSource}
                    onChange={(e) => setNewSource(e.target.value)}
                    placeholder="e.g. Reuters / Nature"
                    className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1">Stance Tag</label>
                  <select
                    value={newStance}
                    onChange={(e) => setNewStance(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
                  >
                    <option value="Supporting">Supporting Fact</option>
                    <option value="Contradicting">Contradicting / Debunked</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Source Reference URL (Optional)</label>
                <input
                  type="url"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  placeholder="https://..."
                  className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-700">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 text-white font-semibold hover:bg-brand-500"
                >
                  Index & Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
