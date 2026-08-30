import React, { useState } from 'react';
import { 
  FlaskConical, 
  Play, 
  BarChart3, 
  ShieldAlert, 
  TrendingDown, 
  Shuffle, 
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { api } from '../services/api';

export const Evaluation: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'benchmark' | 'cross_domain' | 'adversarial'>('benchmark');
  
  // Benchmark Evaluation State
  const [selectedModel, setSelectedModel] = useState('VeritasFusion');
  const [evalSamples, setEvalSamples] = useState(500);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [benchmarkResult, setBenchmarkResult] = useState<any | null>(null);

  // Cross Domain State
  const [trainDomain, setTrainDomain] = useState('politics');
  const [testDomain, setTestDomain] = useState('world');
  const [isCrossEvaluating, setIsCrossEvaluating] = useState(false);
  const [crossDomainResult, setCrossDomainResult] = useState<any | null>(null);

  // Adversarial State
  const [isAdversarialRunning, setIsAdversarialRunning] = useState(false);
  const [adversarialResult, setAdversarialResult] = useState<any | null>(null);

  const handleRunBenchmark = async () => {
    setIsEvaluating(true);
    try {
      const res = await api.runEvaluation({ model_name: selectedModel, sample_limit: evalSamples });
      setBenchmarkResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleRunCrossDomain = async () => {
    setIsCrossEvaluating(true);
    try {
      const res = await api.runCrossDomain({ train_domain: trainDomain, test_domain: testDomain, sample_limit: 200 });
      setCrossDomainResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsCrossEvaluating(false);
    }
  };

  const handleRunAdversarial = async () => {
    setIsAdversarialRunning(true);
    try {
      const res = await api.runAdversarial({ model_name: 'TFIDF_LogisticRegression', sample_limit: 200 });
      setAdversarialResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsAdversarialRunning(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center space-x-2">
          <FlaskConical className="w-7 h-7 text-brand-400" />
          <span>Research Evaluation & Benchmarks</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Rigorous statistical evaluation including calibration curves, cross-domain transfer degradation, and adversarial resilience.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex rounded-xl bg-dark-900 p-1 border border-slate-800">
        <button
          onClick={() => setActiveTab('benchmark')}
          className={`flex-1 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
            activeTab === 'benchmark' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Performance & Calibration Benchmark</span>
        </button>

        <button
          onClick={() => setActiveTab('cross_domain')}
          className={`flex-1 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
            activeTab === 'cross_domain' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <TrendingDown className="w-4 h-4" />
          <span>Cross-Domain Transfer Test</span>
        </button>

        <button
          onClick={() => setActiveTab('adversarial')}
          className={`flex-1 py-2.5 rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 transition-all ${
            activeTab === 'adversarial' ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          <span>Adversarial Perturbation Suite</span>
        </button>
      </div>

      {/* Tab 1: Benchmark */}
      {activeTab === 'benchmark' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 flex flex-col sm:flex-row items-end gap-4">
            <div className="flex-1 space-y-1">
              <label className="text-xs font-semibold text-slate-300">Target Model Architecture</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-200 text-xs"
              >
                <option value="VeritasFusion">VeritasFusion (Multimodal Engine)</option>
                <option value="TFIDF_LogisticRegression">TFIDF + Logistic Regression</option>
                <option value="TFIDF_LinearSVM">TFIDF + Linear SVM</option>
                <option value="PassiveAggressive">Passive Aggressive Classifier</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300">Test Sample Limit</label>
              <input
                type="number"
                value={evalSamples}
                onChange={(e) => setEvalSamples(Number(e.target.value))}
                className="w-32 px-3.5 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-200 text-xs font-mono"
              />
            </div>

            <button
              onClick={handleRunBenchmark}
              disabled={isEvaluating}
              className="px-5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs flex items-center space-x-2 disabled:opacity-50"
            >
              {isEvaluating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>Execute Evaluation</span>
            </button>
          </div>

          {benchmarkResult && (
            <div className="space-y-6">
              {/* Metrics Grid */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-dark-800/90 border border-slate-800 text-center">
                  <span className="text-xs text-slate-400">Macro F1 Score</span>
                  <div className="text-2xl font-bold font-mono text-brand-300 mt-1">{benchmarkResult.macro_f1}</div>
                </div>

                <div className="p-4 rounded-xl bg-dark-800/90 border border-slate-800 text-center">
                  <span className="text-xs text-slate-400">Accuracy</span>
                  <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">{benchmarkResult.accuracy}</div>
                </div>

                <div className="p-4 rounded-xl bg-dark-800/90 border border-slate-800 text-center">
                  <span className="text-xs text-slate-400">ROC-AUC</span>
                  <div className="text-2xl font-bold font-mono text-indigo-300 mt-1">{benchmarkResult.roc_auc}</div>
                </div>

                <div className="p-4 rounded-xl bg-dark-800/90 border border-slate-800 text-center">
                  <span className="text-xs text-slate-400">Calibration Error (ECE)</span>
                  <div className="text-2xl font-bold font-mono text-amber-400 mt-1">{benchmarkResult.expected_calibration_error}</div>
                </div>
              </div>

              {/* Confusion Matrix Table */}
              <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
                  Empirical Confusion Matrix
                </h3>

                <div className="grid grid-cols-2 gap-3 max-w-md mx-auto text-center font-mono text-xs">
                  <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-500/30">
                    <div className="text-slate-400 text-[10px]">True Negatives (Real as Real)</div>
                    <div className="text-xl font-bold text-emerald-400">{benchmarkResult.confusion_matrix.true_negatives}</div>
                  </div>

                  <div className="p-4 rounded-lg bg-rose-950/40 border border-rose-500/30">
                    <div className="text-slate-400 text-[10px]">False Positives (Real as Fake)</div>
                    <div className="text-xl font-bold text-rose-400">{benchmarkResult.confusion_matrix.false_positives}</div>
                  </div>

                  <div className="p-4 rounded-lg bg-rose-950/40 border border-rose-500/30">
                    <div className="text-slate-400 text-[10px]">False Negatives (Fake as Real)</div>
                    <div className="text-xl font-bold text-rose-400">{benchmarkResult.confusion_matrix.false_negatives}</div>
                  </div>

                  <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-500/30">
                    <div className="text-slate-400 text-[10px]">True Positives (Fake as Fake)</div>
                    <div className="text-xl font-bold text-emerald-400">{benchmarkResult.confusion_matrix.true_positives}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Cross Domain */}
      {activeTab === 'cross_domain' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Domain Transfer Generalization Evaluation
            </h3>
            <p className="text-xs text-slate-400">
              Tests how well a model trained on one subject domain transfers to a completely different domain.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-slate-300 mb-1">Source Training Domain</label>
                <input
                  type="text"
                  value={trainDomain}
                  onChange={(e) => setTrainDomain(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-1">Target Evaluation Domain</label>
                <input
                  type="text"
                  value={testDomain}
                  onChange={(e) => setTestDomain(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-dark-900 border border-slate-700 text-slate-100"
                />
              </div>
            </div>

            <button
              onClick={handleRunCrossDomain}
              disabled={isCrossEvaluating}
              className="px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs flex items-center space-x-2 disabled:opacity-50"
            >
              {isCrossEvaluating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>Run Cross-Domain Transfer Experiment</span>
            </button>
          </div>

          {crossDomainResult && (
            <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
              <h4 className="text-sm font-bold text-white">
                Transfer Experiment: {crossDomainResult.train_domain} ➔ {crossDomainResult.test_domain}
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-center text-xs">
                <div className="p-4 rounded-xl bg-dark-900 border border-slate-800">
                  <span className="text-slate-400">In-Domain F1</span>
                  <div className="text-xl font-bold text-emerald-400 mt-1">{crossDomainResult.in_domain_macro_f1}</div>
                </div>

                <div className="p-4 rounded-xl bg-dark-900 border border-slate-800">
                  <span className="text-slate-400">Cross-Domain F1</span>
                  <div className="text-xl font-bold text-indigo-300 mt-1">{crossDomainResult.cross_domain_macro_f1}</div>
                </div>

                <div className="p-4 rounded-xl bg-dark-900 border border-slate-800">
                  <span className="text-slate-400">Performance Drop</span>
                  <div className="text-xl font-bold text-rose-400 mt-1">-{crossDomainResult.f1_performance_degradation_pct}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Adversarial */}
      {activeTab === 'adversarial' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Synthetic Adversarial Robustness Suite
            </h3>
            <p className="text-xs text-slate-400">
              Injects casing anomalies, punctuation jitter, and distractor sentences into test samples to evaluate model resilience.
            </p>

            <button
              onClick={handleRunAdversarial}
              disabled={isAdversarialRunning}
              className="px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs flex items-center space-x-2 disabled:opacity-50"
            >
              {isAdversarialRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              <span>Execute Adversarial Perturbation Suite</span>
            </button>
          </div>

          {adversarialResult && (
            <div className="p-6 rounded-2xl bg-dark-800/90 border border-slate-800 space-y-4">
              <h4 className="text-sm font-bold text-white flex items-center justify-between">
                <span>Adversarial Stress Test: {adversarialResult.model_name}</span>
                <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-brand-500/30 text-brand-300">
                  Resilience Grade: {adversarialResult.adversarial_resilience_grade}
                </span>
              </h4>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-center text-xs">
                <div className="p-3 rounded-lg bg-dark-900 border border-slate-800">
                  <span className="text-slate-400 text-[10px]">Clean F1</span>
                  <div className="text-base font-bold text-emerald-400">{adversarialResult.clean_macro_f1}</div>
                </div>

                <div className="p-3 rounded-lg bg-dark-900 border border-slate-800">
                  <span className="text-slate-400 text-[10px]">Casing Jitter F1</span>
                  <div className="text-base font-bold text-slate-200">{adversarialResult.casing_perturbed_macro_f1}</div>
                </div>

                <div className="p-3 rounded-lg bg-dark-900 border border-slate-800">
                  <span className="text-slate-400 text-[10px]">Punctuation Jitter F1</span>
                  <div className="text-base font-bold text-slate-200">{adversarialResult.punctuation_perturbed_macro_f1}</div>
                </div>

                <div className="p-3 rounded-lg bg-dark-900 border border-slate-800">
                  <span className="text-slate-400 text-[10px]">Noise Injection F1</span>
                  <div className="text-base font-bold text-slate-200">{adversarialResult.distractor_inserted_macro_f1}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
