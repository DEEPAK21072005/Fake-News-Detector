# Research Problem Statement: Multimodal Misinformation & Verification

## 1. Introduction
The proliferation of digital misinformation across online media poses significant risks to public health, democratic institutions, and financial markets. While traditional Natural Language Processing (NLP) systems framed fake news detection primarily as a binary text classification problem, real-world misinformation exhibits complex, cross-modal characteristics:
1. **Stylistic Deception**: Sensationalized vocabulary, clickbait syntax, all-caps emphasis, and emotional valence designed to trigger visceral cognitive bias.
2. **Factual Dissonance**: Objective-sounding, well-structured articles that state fabricated propositions contradicted by established empirical facts.
3. **Multimodal Recontextualization ("Cheapfakes")**: Authentic images paired with fabricated or misleading headlines and captions.

## 2. The Core Taxonomic Distinction: Classification vs. Verification
A fundamental research principle of **VeritasAI** is the explicit architectural decoupling of:

$$\text{Classification} \neq \text{Verification}$$

* **Classification** ($\mathcal{F}_{style}: \mathcal{X}_{text} \rightarrow [0, 1]$):
  Evaluates whether the lexical structure, tone, emotional intensity, and syntactic features of an article resemble historical corpora of deceptive writing.
* **Verification** ($\mathcal{F}_{evidence}: \langle \mathcal{Q}_{claim}, \mathcal{K}_{evidence} \rangle \rightarrow \mathcal{S}_{stance}$):
  Evaluates whether explicit factual claims extracted from the article are corroborated, contradicted, or unaddressed by verified ground-truth knowledge bases.

Conflating these two tasks leads to severe failure modes: a truthful article written passionately may be misclassified as fake, while a completely fabricated claim written in dry, academic tone may be falsely classified as real.

## 3. 4-Tier Verification State Space
To communicate uncertainty honestly without presenting probabilistic scores as infallible truth, VeritasAI maps predictions into a calibrated 4-tier decision state:

$$\mathcal{Y} \in \{\text{LIKELY\_REAL}, \text{LIKELY\_FAKE}, \text{UNCERTAIN}, \text{INSUFFICIENT\_EVIDENCE}\}$$

This guarantees that claims with low evidence density or ambiguous stylistic signals are designated as `UNCERTAIN` or `INSUFFICIENT_EVIDENCE` rather than assigning an overconfident hallucinated binary label.
