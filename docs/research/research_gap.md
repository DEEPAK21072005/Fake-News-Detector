# Research Gaps in Contemporary Fake News Detection Systems

Despite extensive literature on NLP classification, existing automated fact-checking and fake-news detection frameworks suffer from seven critical research limitations:

---

### Gap 1: High In-Domain Benchmark Accuracy vs. Poor Out-of-Distribution Generalization
Many published models report $>95\%$ accuracy on static datasets (e.g., standard splits of ISOT or LIAR). However, when evaluated out-of-distribution across different news domains (e.g., evaluating a politics-trained model on health or science claims), Macro F1 frequently drops by $15\% - 35\%$. Models overfit to topical entity tokens (e.g., politician names) rather than learning invariant stylistic and verification indicators.

### Gap 2: Dataset Leakage via Duplicate / Near-Paraphrased Stories
Public fake news datasets frequently contain near-duplicate articles originating from wire services or syndicated blogs. Standard random train/test splits inadvertently place identical narratives into both partitions, causing severe data leakage and artificially inflated benchmark scores. Group-aware narrative splitting is essential.

### Gap 3: Semantic Similarity Is Not Fact Verification
Standard vector search identifies topical relevance ($\text{CosineSimilarity}(\vec{u}, \vec{v}) > 0.8$), but high semantic similarity does not imply factual agreement. A claim ("Coffee cures cancer") has high vector similarity to a debunking article ("Coffee does not cure cancer"). A verification layer must explicitly model **Stance Directionality** ($\text{Support}$ vs. $\text{Contradict}$).

### Gap 4: Multimodal Out-of-Context Image Reuse ("Cheapfakes")
The majority of multimodal misinformation does not involve synthetic GAN or Diffusion deepfakes, but rather genuine photographs recycled with deceptive headlines. Systems must inspect visual context, OCR text embedded in memes/screenshots, and cross-modal alignment.

### Gap 5: Rapid Temporal Evolution & Breaking News Blindspots
Misinformation evolves continuously. Zero-shot claims on breaking world events have no historical training data. Systems must detect narrative novelty ($\text{Novelty Score}$) rather than assuming unindexed topics are inherently real or fake.

### Gap 6: Overconfidence & Calibration Error
Uncalibrated deep neural networks exhibit poor probability calibration (high Expected Calibration Error, $\text{ECE} > 0.15$), outputting $99\%$ confidence on ambiguous inputs. Post-hoc calibration (Platt Scaling, Isotonic Regression, Temperature Scaling) is necessary.

### Gap 7: Prohibitive Computational Requirements
Many recent multimodal research prototypes require multi-GPU clusters (Llama-3-70B, BLIP-2), making them unusable on consumer laptops and edge devices. VeritasAI establishes a resource-efficient architecture optimized for 16GB RAM CPU execution.
