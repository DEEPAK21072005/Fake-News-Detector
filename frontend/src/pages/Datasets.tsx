import React, { useState, useEffect } from 'react';
import { 
  Database, 
  UploadCloud, 
  FileSpreadsheet, 
  Split, 
  Trash2, 
  Eye,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { DatasetSummary } from '../types';

export const Datasets: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadName, setUploadName] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const fetchDatasets = async () => {
    try {
      const list = await api.listDatasets();
      setDatasets(list);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadName) return;
    setIsUploading(true);
    setStatusMsg(null);

    const formData = new FormData();
    formData.append('name', uploadName);
    formData.append('file', uploadFile);

    try {
      const res = await fetch('/api/datasets/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Upload failed.');
      setStatusMsg('Dataset uploaded and canonical column schemas mapped successfully!');
      setUploadName('');
      setUploadFile(null);
      fetchDatasets();
    } catch (err: any) {
      setStatusMsg(`Upload error: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <Database className="w-7 h-7 text-brand-400" />
          <span>Research Dataset Management</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Ingest CSV, JSON, and JSONL corpora with automated schema mapping and leakage-free narrative splitting.
        </p>
      </div>

      {/* Upload & Ingestion Box */}
      <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
          <UploadCloud className="w-4 h-4 text-brand-400" />
          <span>Upload Custom News Corpus (CSV / JSON / JSONL)</span>
        </h3>

        <form onSubmit={handleUpload} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end text-xs">
          <div>
            <label className="block text-slate-300 mb-1 font-semibold">Dataset Identifier / Name</label>
            <input
              type="text"
              required
              value={uploadName}
              onChange={(e) => setUploadName(e.target.value)}
              placeholder="e.g. WELFake_v2 / GossipCop"
              className="w-full px-3.5 py-2.5 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
            />
          </div>

          <div>
            <label className="block text-slate-300 mb-1 font-semibold">File Path / Select File</label>
            <input
              type="file"
              required
              accept=".csv,.json,.jsonl"
              onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
              className="w-full text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700"
            />
          </div>

          <button
            type="submit"
            disabled={isUploading}
            className="w-full py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-md disabled:opacity-50 transition-colors"
          >
            {isUploading ? 'Parsing & Ingesting...' : 'Upload & Map Schema'}
          </button>
        </form>

        {statusMsg && (
          <div className="p-3 rounded-lg bg-slate-900 border border-brand-500/30 text-slate-200 text-xs flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{statusMsg}</span>
          </div>
        )}
      </div>

      {/* Registered Datasets List */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Available Datasets ({datasets.length + 1})
        </h3>

        {/* Built-in ISOT Corpus Card */}
        <div className="p-5 rounded-xl bg-dark-800/90 border border-brand-500/30 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-lg bg-brand-500/10 text-brand-400">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                  <span>ISOT Fake News Corpus (Primary Benchmark)</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                    Active Benchmark
                  </span>
                </h4>
                <p className="text-xs text-slate-400">File: fake_news_data.csv • 44,898 total articles</p>
              </div>
            </div>

            <div className="text-right font-mono text-xs text-slate-300">
              44,898 Rows • Real & Fake
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800 text-[11px] font-mono text-slate-400">
            <div>Mapped Text: <strong className="text-slate-200">text</strong></div>
            <div>Mapped Title: <strong className="text-slate-200">title</strong></div>
            <div>Mapped Label: <strong className="text-slate-200">label</strong></div>
            <div>Domain/Subject: <strong className="text-slate-200">subject</strong></div>
          </div>
        </div>

        {/* Custom Uploaded Datasets */}
        {datasets.map((ds) => (
          <div key={ds.id} className="p-5 rounded-xl bg-dark-800/90 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-lg bg-slate-800 text-slate-300">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">{ds.name}</h4>
                  <p className="text-xs text-slate-400">Filename: {ds.filename}</p>
                </div>
              </div>

              <div className="text-right font-mono text-xs text-slate-300">
                {ds.row_count} Rows
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800 text-[11px] font-mono text-slate-400">
              <div>Mapped Text: <strong className="text-slate-200">{ds.mapped_columns?.text || 'N/A'}</strong></div>
              <div>Mapped Title: <strong className="text-slate-200">{ds.mapped_columns?.title || 'N/A'}</strong></div>
              <div>Mapped Label: <strong className="text-slate-200">{ds.mapped_columns?.label || 'N/A'}</strong></div>
              <div>Status: <strong className="text-emerald-400">Ingested</strong></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
