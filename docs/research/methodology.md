# Research Methodology: VeritasFusion Architecture

## 1. Feature Representation Pipeline

### 1.1 Stylometric & Linguistic Signal Extraction
For an input document with text $T$ and optional headline $H$, VeritasAI computes a 10-dimensional linguistic representation vector $\mathbf{v}_{ling} \in \mathbb{R}^{10}$:
* **Sensationalism Index ($S_{sens}$)**: Normalized frequency of sensational and conspiratorial keyword matches weighted by rhetorical prominence.
* **Clickbait Index ($S_{click}$)**: Structural match against syntactic clickbait patterns and capitalization anomalies.
* **Uppercase Density ($R_{caps}$)**: Ratio of capitalized tokens to total alpha tokens.
* **Punctuation Anomaly ($S_{punct}$)**: Density of multiple exclamation/question marks ($?!$) normalized per sentence.
* **Sentiment Polarity ($P_{sent}$)**: Balance of positive vs. negative emotional valence lexicon.
* **Emotional Intensity ($I_{emo}$)**: Density of strong affect-bearing tokens.
* **Lexical Diversity ($TTR$)**: Type-Token Ratio ($\frac{|V_{unique}|}{|V_{total}|}$).
* **Average Sentence Length ($\mu_{len}$)**.
* **Normalized Word Count ($\hat{N}_{words}$)**.
* **Sensational Keyword Density ($\hat{N}_{sens}$)**.

### 1.2 Dense Semantic Representation
Using compact transformer encoders (e.g. `all-MiniLM-L6-v2`), articles are chunked into sentence-preserving windows of $L \le 256$ tokens with overlap $o = 32$. Chunk representations $\mathbf{h}_k$ are hierarchically pooled:
$$\mathbf{v}_{text} = \sum_{k=1}^K w_k \mathbf{h}_k, \quad \text{where } w_1 = 1.5 w_k, \quad \|\mathbf{v}_{text}\|_2 = 1$$

### 1.3 Multimodal Visual & OCR Pipeline
* **Visual Perceptual Vector ($\mathbf{v}_{img} \in \mathbb{R}^{128}$)**: Spatial color layout concatenated with channel color histograms and perceptual difference hashing ($dHash$).
* **OCR Text Embedding ($\mathbf{v}_{ocr} \in \mathbb{R}^{384}$)**: Dense semantic encoding of extracted embedded image text.

---

## 2. Retrieval-Augmented Evidence Verification & Narrative Stance
Given primary claim $q$, the vector retrieval engine searches the evidence database $\mathcal{D}$:
$$\mathcal{M}_{top} = \text{Top-K}_{d \in \mathcal{D}} \left( \cos(\mathbf{e}_q, \mathbf{e}_d) \right)$$
Each evidence item is weighted by source authority credibility $\omega(d) \in [0.4, 0.99]$.
The net evidence polarity signal is computed as:
$$\Delta_{ev} = \max_{d \in \mathcal{M}_{contra}} (\cos(\mathbf{e}_q, \mathbf{e}_d) \cdot \omega(d)) - \max_{d \in \mathcal{M}_{supp}} (\cos(\mathbf{e}_q, \mathbf{e}_d) \cdot \omega(d))$$

---

## 3. Multimodal Fusion & Confidence Calibration

### 3.1 VeritasFusion Decision Layer
The combined cross-modal representation $\mathbf{x}_{fused} = [\mathbf{v}_{text} \,\|\, \mathbf{v}_{ling} \,\|\, \mathbf{v}_{img} \,\|\, \mathbf{v}_{ev} \,\|\, \mathbf{v}_{narr}]$ is mapped through a regularized classification head to yield raw probability $\hat{p} = P(Fake \mid \mathbf{x})$.

### 3.2 Post-Hoc Calibration (Platt Scaling)
Raw logits $z = \ln(\frac{\hat{p}}{1 - \hat{p}})$ are calibrated via:
$$p_{calib} = \frac{1}{1 + \exp(- (a z + b))}$$
where parameters $a, b$ are optimized by minimizing Negative Log-Likelihood on held-out validation data.
