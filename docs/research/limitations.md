# Research Limitations & Ethical Considerations

## 1. Systemic Limitations

### 1.1 Satire and Irony Detection
Satirical content (e.g., The Onion, Babylon Bee) intentionally utilizes sensationalism and absurd premises as comedic devices. Automated classifiers frequently misclassify high-quality satire as malicious fake news unless explicitly provided domain metadata.

### 1.2 Breaking News Cold-Start Problem
Emerging, rapidly unfolding geopolitical or environmental events have zero pre-indexed verification evidence. In such scenarios, the system must output `INSUFFICIENT_EVIDENCE` or `UNCERTAIN` rather than forcing a low-confidence decision.

### 1.3 Sophisticated Factual Fabrications
Deceptive articles written in sober, academic, or formal journalistic prose without sensational vocabulary bypass stylistic classifiers. In these instances, verification performance is entirely bounded by evidence database completeness.

---

## 2. Ethical Principles & Human-in-the-Loop Architecture
* **Non-Censorship**: VeritasAI is designed strictly as an epistemic decision-support tool for journalists, researchers, and citizens. It does not automate content moderation or censorship.
* **Uncertainty Transparency**: The platform explicitly displays evidence strength and reliability metrics rather than binary declarations of absolute truth.
