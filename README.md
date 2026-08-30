# VeritasAI: Multimodal Fake News Detection & Verification Platform

> **A research-grade, resource-aware Multimodal Fake News Detection and Evidence Verification Platform designed for CPU execution (Intel Core i5-1340P, 16 GB RAM, Windows 11).**

---

## 1. System Overview & Core Research Philosophy

**VeritasAI** is an epistemic verification system that strictly decouples:
1. **Classification** (*"Does this article exhibit linguistic, stylometric, and emotional patterns characteristic of deceptive content?"*)
2. **Verification** (*"Is there corroborating or contradicting empirical evidence in verified knowledge repositories for the extracted claim?"*)

Rather than presenting black-box softmax probabilities as infallible truth, VeritasAI outputs calibrated confidence scores across a 4-tier decision taxonomy:
* `LIKELY_REAL`
* `LIKELY_FAKE`
* `UNCERTAIN`
* `INSUFFICIENT_EVIDENCE`

---

## 2. System Architecture

```text
                               ┌──────────────────────────────────┐
                               │           Web Client             │
                               │      React 18 + TypeScript       │
                               └────────────────┬─────────────────┘
                                                │ REST / JSON
                                                ▼
                               ┌──────────────────────────────────┐
                               │          FastAPI Backend         │
                               └────────────────┬─────────────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
┌──────────────────┐                  ┌───────────────────┐                  ┌──────────────────┐
│  Text & Stylometry│                  │  Vision & OCR     │                  │  Vector Retrieval│
│  - Sensationalism│                  │  - Perceptual Hash│                  │  - Cosine Search │
│  - Clickbait Index│                 │  - Color Histograms│                 │  - Stance Tagging│
│  - MiniLM Encoder│                  │  - OCR Extraction │                  │  - Narrative Clust│
└────────┬─────────┘                  └─────────┬─────────┘                  └─────────┬────────┘
         │                                      │                                      │
         └──────────────────────────────────────┼──────────────────────────────────────┘
                                                ▼
                               ┌──────────────────────────────────┐
                               │         VeritasFusion            │
                               │     Multimodal Fusion Head       │
                               └────────────────┬─────────────────┘
                                                ▼
                               ┌──────────────────────────────────┐
                               │       Confidence Calibration     │
                               │     (Platt / Isotonic / Temp)    │
                               └────────────────┬─────────────────┘
                                                ▼
                               ┌──────────────────────────────────┐
                               │       Explainability Engine      │
                               │     (Token Highlighting + Cards) │
                               └──────────────────────────────────┘
```

---

## 3. Key Research Features

* **Linguistic Stylometry Engine**: Extracts exact metrics for sensationalism, clickbait structure, uppercase ratio, punctuation anomalies, sentiment polarity, emotional intensity, and syntactic claim propositions.
* **Hierarchical Document Chunking**: Splits lengthy news reports into 256-token sentence-preserving windows with overlap, preventing OOM errors on CPU.
* **Retrieval-Augmented Verification**: Vector search over indexed evidence with source authority weighting (Reuters, BBC, Nature = 0.95+).
* **Narrative Consistency & Novelty**: Calculates exact empirical distribution (`Consistent %`, `Contradictory %`, `Novel %`) against narrative clusters.
* **Multimodal Gating Breakdown**: Dynamically computes exact decision influence (`Text %`, `Image %`, `Evidence %`).
* **Hardware & Resource Safety**: Lazy loading, batch size bounding, and memory monitoring tailored for 16GB RAM laptops.
* **No Fake Metrics / Placeholders**: All calibration curves, token attributions, confusion matrices, and ablation tables are computed dynamically.

---

## 4. Models Supported & Benchmarks

| Model Architecture | Description | Optimal Use Case |
| :--- | :--- | :--- |
| **TFIDF_LogisticRegression** | TF-IDF (unigrams + bigrams) + L2 Regularization | Fast statistical baseline (~15ms) |
| **TFIDF_LinearSVM** | TF-IDF + Calibrated Linear Support Vector Machine | Linear margin baseline with calibration |
| **PassiveAggressive** | Online learning Passive-Aggressive classifier | High-throughput streaming baseline |
| **VeritasFusion** | Multimodal Dense Semantics + Stylometry + Evidence Stance | Flagship verification architecture |

---

## 5. Quickstart Guide (Windows 11 PowerShell)

### Prerequisites
* Python 3.10+ (Tested on Python 3.12.10)
* Node.js v18+ & npm (Tested on Node v22.18.0)

### 1. Install Backend Dependencies
```powershell
pip install -r backend/requirements.txt
```

### 2. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### 3. Seed Evidence & Train Baseline Models
```powershell
python scripts/seed_evidence.py
python scripts/train_starter_models.py
```

### 4. Run Automated Test Suite
```powershell
python -m pytest backend/tests -v
```

### 5. Launch Full Stack with One Command
```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
```
* **Frontend Web Dashboard**: `http://localhost:5173`
* **FastAPI Backend API & Docs**: `http://localhost:8000/docs`

---

## 6. Academic Research Documentation

Master's-level research papers and methodology documents are available in `docs/research/`:
* [`problem_statement.md`](docs/research/problem_statement.md) - Formal problem definition & classification vs verification distinction
* [`research_gap.md`](docs/research/research_gap.md) - Analysis of 7 critical research gaps in modern misinformation detection
* [`methodology.md`](docs/research/methodology.md) - Mathematical formulation of VeritasFusion and feature extraction
* [`architecture.md`](docs/research/architecture.md) - Resource-aware micro-architecture & memory profiles
* [`experiments.md`](docs/research/experiments.md) - Experimental protocol & ablation matrix
* [`evaluation.md`](docs/research/evaluation.md) - ECE calibration, group-aware splitting, and metrics suite
* [`limitations.md`](docs/research/limitations.md) - Satire, cold-start breaking news, and epistemic boundaries
* [`future_work.md`](docs/research/future_work.md) - Temporal Knowledge Graphs & Cross-Attention Alignment

---

## 7. License & Ethical Disclaimer

VeritasAI is an epistemic decision-support research tool designed to assist human fact-checkers, journalists, and researchers. It does not automate content censorship and explicitly presents uncertainty metrics on ambiguous or emerging claims.
