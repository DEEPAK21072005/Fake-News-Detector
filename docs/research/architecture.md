# System Architecture & Resource Optimization

## 1. High-Level Modular Design
VeritasAI employs a decoupled, asynchronous micro-architecture designed for local CPU execution within 16GB RAM:

```text
┌─────────────────────────────────────────────────────────────┐
│                   Web Client (React + TS)                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Router                   │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│      ML & Fusion Engine      │ │   Local Retrieval Engine   │
│  - Stylometric Feature Extr. │ │  - LocalVectorStore (CPU)  │
│  - MiniLM Sentence Encoder   │ │  - Stance Alignment        │
│  - MobileNet / Visual pHash  │ │  - Narrative Consistency   │
│  - Platt Scaler Calibrator   │ └─────────────┬──────────────┘
└──────────────┬───────────────┘               │
               └───────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Explainability & Synthesis                │
│       (Token Attribution Highlighter + Model Cards)         │
└─────────────────────────────────────────────────────────────┘
```

## 2. Resource Manager & Memory Safety Profile
For an Intel Core i5-1340P (16GB RAM) environment:
1. **Lazy Loading**: Models are not all instantiated at boot time. Embedders and vision models are loaded only upon their first request and tracked via `ResourceManager`.
2. **Document Chunking with Sentence Boundaries**: Prevents Out-Of-Memory (OOM) errors on long documents by bounding transformer inputs to 256 tokens.
3. **In-Memory Zero-Copy Vector Search**: Vector lookups are vectorized in NumPy with BLAS acceleration, avoiding external database server overhead.
