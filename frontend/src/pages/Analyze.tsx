import React, { useState } from 'react';
import { 
  FileText, 
  Globe, 
  Image as ImageIcon, 
  UploadCloud, 
  Sparkles, 
  CheckCircle2, 
  Layers, 
  AlertCircle,
  Loader2,
  X
} from 'lucide-react';
import { api } from '../services/api';
import { AnalysisResponse } from '../types';

interface AnalyzeProps {
  onAnalysisComplete: (result: AnalysisResponse) => void;
}

const DEMO_SAMPLES = [
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

export const Analyze: React.FC<AnalyzeProps> = ({ onAnalysisComplete }) => {
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

  const handleLoadSample = (sample: typeof DEMO_SAMPLES[0]) => {
    setInputMode('text');
    setTitle(sample.title);
    setText(sample.text);
    setCategory(sample.category);
    setErrorMsg(null);
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsProcessing(true);
    setCurrentStage(0);

    // Dynamic progress stepper simulator
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
        onAnalysisComplete(result);
      }, 300);

    } catch (err: any) {
      clearInterval(stageInterval);
      setIsProcessing(false);
      setErrorMsg(err.message || 'An error occurred during verification.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          Verify Content & Fact Analysis
        </h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Submit article text, public news URLs, or multimodal images with embedded claims for research verification.
        </p>
      </div>

      {/* Demo Benchmark Samples Bar */}
      <div className="p-4 rounded-xl bg-dark-800/80 border border-slate-800 space-y-2.5">
        <div className="flex items-center justify-between text-xs">
          <span className="font-semibold text-slate-300 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>Load Quick Benchmark Samples:</span>
          </span>
          <span className="text-slate-500">Click to autofill workspace</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          {DEMO_SAMPLES.map((sample) => (
            <button
              key={sample.id}
              type="button"
              onClick={() => handleLoadSample(sample)}
              className="p-2.5 rounded-lg bg-dark-900/90 border border-slate-800 hover:border-brand-500/50 transition-all text-left group"
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${sample.badgeColor}`}>
                  {sample.badge}
                </span>
                <span className="text-[10px] text-slate-500">{sample.category}</span>
              </div>
              <p className="text-xs text-slate-300 group-hover:text-white line-clamp-1 font-medium">
                {sample.title}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Main Workspace Card */}
      <div className="bg-dark-800/90 rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-xl space-y-6">
        {/* Mode Switcher Tabs */}
        <div className="flex rounded-xl bg-dark-900 p-1 border border-slate-800">
          <button
            type="button"
            onClick={() => setInputMode('text')}
            className={`flex-1 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
              inputMode === 'text' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Article Text / Claim</span>
          </button>
          <button
            type="button"
            onClick={() => setInputMode('url')}
            className={`flex-1 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
              inputMode === 'url' ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>News Article URL</span>
          </button>
          <button
            type="button"
            onClick={() => setInputMode('multimodal')}
            className={`flex-1 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
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
              <label className="text-xs font-semibold text-slate-300 block">News URL to Scrape & Verify</label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.reuters.com/world/article-example..."
                className="w-full px-4 py-3 rounded-xl bg-dark-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm font-mono"
              />
              <p className="text-[11px] text-slate-500">
                Safe SSRF-protected scraper extracts headline, body paragraphs, and source domain metadata automatically.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1.5">Article Headline / Claim Title (Optional)</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Clinical study confirms vaccine efficacy..."
                  className="w-full px-4 py-2.5 rounded-xl bg-dark-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1.5">Full Article Content / Assertion Body</label>
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
              <label className="text-xs font-semibold text-slate-300 block">Multimodal News Photograph / Screenshot (Optional)</label>
              
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
                  <span className="text-xs font-semibold text-slate-200">Click to upload or drag image here</span>
                  <span className="text-[11px] text-slate-500 mt-0.5">PNG, JPG, WEBP up to 10MB</span>
                  <input type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                </label>
              )}
            </div>
          )}

          {/* Configuration Controls Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800">
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1">Subject Area</label>
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
              <label className="text-xs font-semibold text-slate-400 block mb-1">Inference Mode Profile</label>
              <select
                value={inferenceMode}
                onChange={(e) => setInferenceMode(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-brand-500 font-mono"
              >
                <option value="FAST">FAST (Statistical TF-IDF + Stylometry)</option>
                <option value="BALANCED">BALANCED (MiniLM + VeritasFusion + Evidence)</option>
                <option value="RESEARCH">RESEARCH (Full Multimodal + Token Explainability)</option>
                <option value="CLOUD_ENHANCED">CLOUD_ENHANCED (Optional LLM Reasoning Synthesis)</option>
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

          {/* Live Progress Stage Stepper */}
          {isProcessing && (
            <div className="p-5 rounded-xl bg-dark-900 border border-brand-500/30 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-brand-300">
                <span className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-brand-400" />
                  <span>Processing Verification Pipeline...</span>
                </span>
                <span className="font-mono">Stage {currentStage + 1} of {stages.length}</span>
              </div>

              <div className="space-y-1.5 text-xs">
                {stages.map((stg, i) => (
                  <div 
                    key={i} 
                    className={`flex items-center space-x-2 font-mono text-[11px] ${
                      i < currentStage ? 'text-emerald-400' :
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

          {/* Submit Action Button */}
          <button
            type="submit"
            disabled={isProcessing}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-bold text-sm shadow-xl shadow-brand-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Executing Multimodal Pipeline...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze & Verify Content</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
