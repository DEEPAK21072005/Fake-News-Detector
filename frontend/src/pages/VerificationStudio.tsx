import React, { useState } from 'react';
import { 
  FileText, 
  Globe, 
  Image as ImageIcon, 
  Sparkles, 
  ShieldAlert, 
  ShieldCheck, 
  HelpCircle, 
  CheckCircle2, 
  Layers, 
  ArrowRight,
  UploadCloud, 
  X, 
  Loader2, 
  Download, 
  RotateCcw,
  AlertCircle,
  Clock,
  Gauge,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { AnalysisResponse, VerdictType } from '../types';
import { VerdictCard } from '../components/VerdictCard';
import { ClaimList } from '../components/ClaimList';
import { EvidenceList } from '../components/EvidenceList';
import { NarrativePanel } from '../components/NarrativePanel';
import { ModalityBreakdown } from '../components/ModalityBreakdown';
import { LinguisticRadar } from '../components/LinguisticRadar';
import { TokenAttributionHighlighter } from '../components/TokenAttributionHighlighter';

const BENCHMARK_SAMPLES = [
  {
    id: 'sample_real',
    title: 'Kurds offer joint border deployment as Iraq threatens offensive',
    category: 'World',
    badge: 'Likely Real Benchmark',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    text: 'BAGHDAD (Reuters) - Kurdish authorities offered on Tuesday a joint border deployment with Iraqi federal forces at the Fish-Khabur crossing point with Turkey, as Baghdad threatened to resume military operations. The proposal was presented during military talks between Iraqi government commanders and the Peshmerga in the northern city of Mosul. Iraqi Prime Minister Haider al-Abadi ordered a truce on Friday to allow talks with the Kurds on the deployment of federal forces to all disputed areas.'
  },
  {
    id: 'sample_fake',
    title: 'SHOCKING SECRET: Scientists Discover Coffee Miracle Cures ALL Cancers They Don\'t Want You To Know!',
    category: 'Health',
    badge: 'Likely Fake Benchmark',
    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    text: 'BOMBSHELL REVELATION! Deep state medical insiders have been caught hiding the mind-blowing truth from the public! Top secret laboratory experiments have 100% PROVEN that drinking three cups of coffee every morning completely destroys every cancer cell in the human body instantly! The corrupt pharmaceutical industry and mainstream media are desperately trying to ban this unbelievable secret to protect their trillions in profits! SHARE THIS URGENT WARNING BEFORE THEY DELETE IT FOREVER!'
  },
  {
    id: 'sample_uncertain',
    title: 'Speculative unconfirmed rumors circulate regarding confidential diplomatic dialogue',
    category: 'Politics',
    badge: 'Uncertain / Emerging',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    text: 'Anonymous social media accounts and speculative foreign policy blogs are claiming that high-level confidential talks between unnamed foreign emissaries may have taken place in an undisclosed European capital last weekend. Officials from both ministries declined to comment on the unconfirmed rumors, stating that routine diplomatic communications remain ongoing through established regular channels.'
  }
];

export const VerificationStudio: React.FC = () => {
  const [inputMode, setInputMode] = useState<'text' | 'url' | 'multimodal'>('text');
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [category, setCategory] = useState('General');
  const [inferenceMode, setInferenceMode] = useState('BALANCED');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);

  const stages = [
    'Preprocessing & Input Sanitization',
    'Extracting Syntactic Claim Assertions',
    'Computing Transformer Text Embeddings',
    'Extracting Visual Features & OCR Tokens',
    'Retrieving Stance-Aligned Evidence',
    'Evaluating Narrative Consistency',
    'VeritasFusion Multimodal Synthesis',
    'Calibrating Confidence & Attributions'
  ];

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleLoadSample = (sample: typeof BENCHMARK_SAMPLES[0]) => {
    setInputMode('text');
    setTitle(sample.title);
    setText(sample.text);
    setCategory(sample.category);
    setErrorMsg(null);
  };

  const handleClear = () => {
    setTitle('');
    setText('');
    setUrl('');
    setImageFile(null);
    setImagePreview(null);
    setAnalysisResult(null);
    setErrorMsg(null);
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsProcessing(true);
    setCurrentStage(0);

    const stageInterval = setInterval(() => {
      setCurrentStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 450);

    try {
      let result: AnalysisResponse;
      if (inputMode === 'url') {
        if (!url.trim()) throw new Error('Please enter a valid news URL.');
        result = await api.analyzeUrl({ url, category, inference_mode: inferenceMode });
      } else if (inputMode === 'multimodal' && imageFile) {
        const formData = new FormData();
        formData.append('text', text || title);
        if (title) formData.append('title', title);
        formData.append('category', category);
        formData.append('inference_mode', inferenceMode);
        formData.append('image', imageFile);
        result = await api.analyzeMultimodal(formData);
      } else {
        if (!text.trim() && !title.trim()) throw new Error('Please enter article text or claim assertion.');
        result = await api.analyzeText({ text, title, category, inference_mode: inferenceMode });
      }

      clearInterval(stageInterval);
      setCurrentStage(stages.length - 1);
      setTimeout(() => {
        setIsProcessing(false);
        setAnalysisResult(result);
        // Smooth scroll to results
        window.scrollTo({ top: 450, behavior: 'smooth' });
      }, 300);

    } catch (err: any) {
      clearInterval(stageInterval);
      setIsProcessing(false);
      setErrorMsg(err.message || 'An error occurred during verification.');
    }
  };

  const handleExportJSON = () => {
    if (!analysisResult) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analysisResult, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `veritas_verification_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-10 max-w-5xl mx-auto pb-16">
      {/* Hero Header */}
      <div className="text-center space-y-3 pt-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Epistemic Multimodal Verification Studio</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white font-sans">
          Verify News Authenticity & Evidence
        </h1>
        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Decoupling stylistic deception classification from retrieval-augmented evidence verification, 
          narrative consistency, and token-level explainability.
        </p>
      </div>

      {/* 1-Click Benchmark Loaders */}
      <div className="p-4 rounded-2xl bg-dark-800/80 border border-slate-800/90 shadow-lg space-y-2.5">
        <div className="flex items-center justify-between text-xs">
          <span className="font-semibold text-slate-300 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>Load Quick Benchmark Samples:</span>
          </span>
          <span className="text-slate-500">1-click test suite</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          {BENCHMARK_SAMPLES.map((sample) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => handleLoadSample(sample)}
              className="p-3 rounded-xl bg-dark-900/90 border border-slate-800 hover:border-brand-500/50 hover:bg-dark-900 transition-all text-left group cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${sample.badgeColor}`}>
                  {sample.badge}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">{sample.category}</span>
              </div>
              <p className="text-xs text-slate-300 group-hover:text-white line-clamp-1 font-medium">
                {sample.title}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Main Verification Input Workspace */}
      <div className="bg-dark-800/90 rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-2xl space-y-6">
        {/* Mode Switcher Tabs */}
        <div className="flex rounded-xl bg-dark-900 p-1.5 border border-slate-800">
          <button
            type="button"
            onClick={() => setInputMode('text')}
            className={`flex-1 py-2.5 rounded-lg text-xs font-bold flex items-center justify-center space-x-2 transition-all ${
              inputMode === 'text' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Article Text / Claim Body</span>
          </button>
          <button
            type="button"
            onClick={() => setInputMode('url')}
            className={`flex-1 py-2.5 rounded-lg text-xs font-bold flex items-center justify-center space-x-2 transition-all ${
              inputMode === 'url' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>News Article URL</span>
          </button>
          <button
            type="button"
            onClick={() => setInputMode('multimodal')}
            className={`flex-1 py-2.5 rounded-lg text-xs font-bold flex items-center justify-center space-x-2 transition-all ${
              inputMode === 'multimodal' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ImageIcon className="w-4 h-4" />
            <span>Multimodal (Image + Text)</span>
          </button>
        </div>

        {/* Input Form */}
        <form onSubmit={handleAnalyze} className="space-y-5">
          {inputMode === 'url' ? (
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-300 block">News URL to Scrape & Verify</label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.reuters.com/world/example-article..."
                className="w-full px-4 py-3 rounded-xl bg-dark-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm font-mono"
              />
              <p className="text-[11px] text-slate-500">
                SSRF-protected scraper extracts headline, paragraphs, and publisher domain automatically.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Article Headline / Claim Assertion (Optional)</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Health Ministry confirms new clinical trials..."
                  className="w-full px-4 py-2.5 rounded-xl bg-dark-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-slate-300">Article Content / Statement Body</label>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {text.split(/\s+/).filter(Boolean).length} Words
                  </span>
                </div>
                <textarea
                  rows={6}
                  required={inputMode !== 'multimodal' || !imageFile}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste article body text, paragraph statements, or claim assertion..."
                  className="w-full px-4 py-3 rounded-xl bg-dark-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm font-sans leading-relaxed resize-y"
                />
              </div>
            </div>
          )}

          {/* Multimodal Image Drag-and-Drop */}
          {inputMode === 'multimodal' && (
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-300 block">News Photograph / Screenshot (Optional)</label>
              
              {imagePreview ? (
                <div className="relative rounded-xl overflow-hidden border border-slate-700 bg-dark-900 p-2 flex items-center space-x-4">
                  <img src={imagePreview} alt="Preview" className="h-24 w-36 object-cover rounded-lg" />
                  <div className="space-y-1 flex-1 text-xs">
                    <p className="font-semibold text-slate-200">{imageFile?.name}</p>
                    <p className="text-slate-500 font-mono">{Math.round((imageFile?.size || 0) / 1024)} KB</p>
                    <span className="text-[10px] text-emerald-400 font-mono">Ready for Perceptual + OCR extraction</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => { setImageFile(null); setImagePreview(null); }}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-700 hover:border-brand-500 rounded-xl cursor-pointer bg-dark-900/50 hover:bg-dark-900 transition-all">
                  <UploadCloud className="w-8 h-8 text-slate-400 mb-2" />
                  <span className="text-xs font-semibold text-slate-200">Click to upload or drag news image here</span>
                  <span className="text-[11px] text-slate-500 mt-0.5">PNG, JPG, WEBP up to 10MB</span>
                  <input type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                </label>
              )}
            </div>
          )}

          {/* Configuration Controls Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800">
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1">Subject Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                <option value="General">General News</option>
                <option value="Politics">Politics & Elections</option>
                <option value="Health">Health & Medicine</option>
                <option value="Science">Science & Climate</option>
                <option value="Technology">Technology & AI</option>
                <option value="World">World & Geopolitics</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1">Inference Engine Profile</label>
              <select
                value={inferenceMode}
                onChange={(e) => setInferenceMode(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-brand-500 font-mono"
              >
                <option value="BALANCED">BALANCED (MiniLM + VeritasFusion + Evidence - Recommended)</option>
                <option value="FAST">FAST (Statistical TF-IDF + Stylometry ~15ms)</option>
                <option value="RESEARCH">RESEARCH (Full Multimodal + Token Explainability)</option>
                <option value="CLOUD_ENHANCED">CLOUD_ENHANCED (Optional Cloud LLM Synthesis)</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Real-time Progress Stepper */}
          {isProcessing && (
            <div className="p-5 rounded-xl bg-dark-900 border border-brand-500/30 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-brand-300">
                <span className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
                  <span>Executing Verification Pipeline...</span>
                </span>
                <span className="font-mono">Stage {currentStage + 1} of {stages.length}</span>
              </div>

              <div className="space-y-1.5 text-xs">
                {stages.map((stg, i) => (
                  <div 
                    key={i} 
                    className={`flex items-center space-x-2 font-mono text-[11px] ${
                      i < currentStage ? 'text-emerald-400 font-semibold' :
                      i === currentStage ? 'text-brand-300 font-bold' : 'text-slate-600'
                    }`}
                  >
                    <span>{i < currentStage ? '✓' : i === currentStage ? '▶' : '○'}</span>
                    <span>{stg}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={isProcessing}
              className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-600 hover:from-brand-500 hover:to-indigo-500 text-white font-black text-sm shadow-xl shadow-brand-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 cursor-pointer"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying Content...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Verify Content & Explain Prediction</span>
                </>
              )}
            </button>

            {(text || title || url || imageFile || analysisResult) && (
              <button
                type="button"
                onClick={handleClear}
                className="px-4 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer"
                title="Clear Workspace"
              >
                <RotateCcw className="w-4 h-4" />
                <span className="hidden sm:inline">Reset</span>
              </button>
            )}
          </div>
        </form>
      </div>

      {/* ========================================================================= */}
      {/* Peak Results Section */}
      {/* ========================================================================= */}
      {analysisResult && (
        <div className="space-y-6 pt-4 border-t border-slate-800/80">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-brand-400 animate-pulse"></span>
              <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight font-sans">
                Verification Report & Epistemic Breakdown
              </h2>
            </div>

            <button
              onClick={handleExportJSON}
              className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300 hover:text-white px-3.5 py-2 rounded-xl bg-dark-800 border border-slate-700 hover:border-slate-600 transition-colors shadow-md cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Report (JSON)</span>
            </button>
          </div>

          {/* Large High-Impact Verdict Card */}
          <VerdictCard analysis={analysisResult} />

          {/* Optional AI Synthesis Summary */}
          {analysisResult.llm_synthesis && (
            <div className="p-5 rounded-xl bg-gradient-to-r from-brand-950/40 via-dark-800 to-dark-800 border border-brand-500/30 space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-brand-300 uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-brand-400" />
                <span>Verification Synthesis ({analysisResult.llm_synthesis.provider})</span>
              </div>
              <p className="text-sm text-slate-200 leading-relaxed font-sans">
                {analysisResult.llm_synthesis.summary}
              </p>
            </div>
          )}

          {/* 2-Column Grid: Multimodal Gating Breakdown & Linguistic Stylometry */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ModalityBreakdown breakdown={analysisResult.modality_breakdown} />
            <LinguisticRadar signals={analysisResult.linguistic_signals} />
          </div>

          {/* Syntactic Claim Assertions */}
          <ClaimList claims={analysisResult.claims} />

          {/* Verified Evidence (Supporting / Contradicting) */}
          <EvidenceList
            supporting={analysisResult.supporting_evidence}
            contradicting={analysisResult.contradicting_evidence}
            related={analysisResult.related_evidence}
          />

          {/* Narrative Consistency & Novelty Spread */}
          <NarrativePanel narrative={analysisResult.narrative_consistency} />

          {/* Explainable Token Attribution Cloud */}
          <TokenAttributionHighlighter attributions={analysisResult.token_attributions} />

          {/* Research Limitations & Ethical Disclaimers */}
          <div className="p-5 rounded-xl bg-dark-900/90 border border-slate-800 text-xs space-y-2.5">
            <h4 className="font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              <span>Research Limitations & Epistemic Disclaimers</span>
            </h4>
            <ul className="space-y-1.5 text-slate-400 text-[11px] leading-relaxed">
              {analysisResult.limitations.map((lim, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <span className="text-slate-500">•</span>
                  <span>{lim}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
