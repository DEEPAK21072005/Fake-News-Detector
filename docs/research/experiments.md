# Experimental Design & Ablation Protocol

## 1. Experimental Objectives
The experimental suite is structured around three research hypotheses:
* **H1 (Multimodal Superiority)**: Incorporating cross-modal visual representations and stylometric signals achieves superior Macro F1 over isolated dense text representations alone.
* **H2 (Retrieval Stance Alignment)**: Grounding classifications against an indexed verified evidence database reduces false positives on factual claims.
* **H3 (Cross-Domain Robustness)**: Stylometric feature gating mitigates performance degradation when transferring models across news domains.

## 2. Experimental Configurations (Ablation Matrix)

| Experiment ID | Configuration Name | Features / Modalities Active |
| :--- | :--- | :--- |
| **EXP-01** | Text Only (TF-IDF Baselines) | TF-IDF (1-2 n-grams) + Logistic Regression / SVM |
| **EXP-02** | Text Dense Embeddings | `all-MiniLM-L6-v2` dense vectors ($d=384$) |
| **EXP-03** | Text + Stylometric Cues | Dense Embeddings + Sensationalism + Clickbait + Uppercase |
| **EXP-04** | Text + Retrieval Stance | Dense Embeddings + Stylometry + Vector Evidence Alignment |
| **EXP-05** | Text + Narrative Consistency | Dense Embeddings + Stylometry + Narrative Distribution |
| **EXP-06** | **Full VeritasFusion** | Text + Stylometry + Vision + OCR + Evidence + Narrative |

## 3. Adversarial Perturbation Suite
Models are systematically subjected to 4 synthetic adversarial stress tests:
1. **Casing Inversion**: 20% random uppercase/lowercase flips.
2. **Punctuation Jitter**: Insertion of sensational punctuation patterns ($?!$, $...$).
3. **Noise Distractor Insertion**: Neutral, irrelevant factual sentences injected into article midpoints.
4. **Synonym Paraphrasing**: Replacement of lexical triggers with semantic equivalents.
