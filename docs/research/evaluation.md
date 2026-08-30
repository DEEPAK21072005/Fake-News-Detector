# Evaluation Metrics & Generalization Framework

## 1. Metrics Suite

### 1.1 Macro-Averaged F1
To prevent majority-class bias on imbalanced datasets, VeritasAI prioritizes Macro F1 over simple Accuracy:
$$\text{Macro F1} = \frac{1}{C} \sum_{c=1}^C \frac{2 \cdot P_c \cdot R_c}{P_c + R_c}$$

### 1.2 Expected Calibration Error (ECE)
Measures the correspondence between predicted confidence $\hat{p}$ and actual empirical accuracy across $M$ equal-interval probability bins $B_m$:
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 1.3 Area Under the Precision-Recall Curve (PR-AUC) & ROC-AUC
Evaluates ranking quality across varying decision thresholds, especially for rare class detection.

---

## 2. Leakage-Free Dataset Partitioning
* **Group-Aware Splitting**: For datasets containing recurring stories, samples are grouped by normalized headline hash clusters before partitioning, preventing train/test contamination.
* **Stratified K-Fold Cross Validation**: Guarantees identical class balance across folds for baseline comparisons.
