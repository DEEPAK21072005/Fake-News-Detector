import re
from typing import Dict, Any, List
from backend.app.ml.preprocessing import SENSATIONAL_KEYWORDS, POSITIVE_LEXICON, NEGATIVE_LEXICON, normalize_tokens


class PredictionExplainer:
    """
    Explainability Engine: Token-level importance attribution,
    feature-level influence scoring, and research limitations generator.
    """
    def explain_text_signals(self, text: str, linguistic_signals: Dict[str, Any], top_k: int = 15) -> List[Dict[str, Any]]:
        """
        Calculates exact word attribution scores based on sensationalism, sentiment polarity,
        capitalization, and stylistic weights.
        """
        words = re.findall(r'\b[A-Za-z0-9\'-]+\b', text)
        if not words:
            return []

        attributions = []
        for word in words:
            w_lower = word.lower()
            score = 0.0
            reasons = []

            # Sensational trigger words contribute towards Fake (+ score)
            if w_lower in SENSATIONAL_KEYWORDS:
                score += 0.45
                reasons.append("Sensational trigger keyword")

            # Negative emotionally charged words
            if w_lower in NEGATIVE_LEXICON:
                score += 0.20
                reasons.append("Negative emotional valence")

            # Positive/Neutral verified indicators contribute towards Real (- score)
            if w_lower in POSITIVE_LEXICON:
                score -= 0.35
                reasons.append("Neutral/credible journalistic indicator")

            # All-caps emphasis
            if len(word) > 1 and word.isupper():
                score += 0.25
                reasons.append("All-caps emphasis anomaly")

            if abs(score) > 0.05:
                attributions.append({
                    "token": word,
                    "score": round(score, 3),
                    "polarity": "Fake-indicative" if score > 0 else "Real-indicative",
                    "reasons": reasons
                })

        # Sort by absolute impact
        attributions.sort(key=lambda x: abs(x["score"]), reverse=True)
        return attributions[:top_k]

    def generate_limitations(self, verdict: str, evidence_strength: str, has_image: bool) -> List[str]:
        """
        Generates honest, research-grounded limitations for the verification report.
        """
        limitations = [
            "This assessment is an AI-assisted evaluation based on stylistic patterns and retrieved evidence, not an infallible fact determination.",
            "Domain Shift: Models trained on specific news corpora (e.g. ISOT) may exhibit degradation on fast-evolving breaking news.",
            "Linguistic Style vs. Factual Ground Truth: An article can be written in professional neutral prose while containing false factual claims.",
        ]

        if evidence_strength in ("Weak", "None"):
            limitations.append("Incomplete Evidence: The local verification database had limited indexed coverage for this specific subject.")

        if has_image:
            limitations.append("Multimodal Context: Image analysis inspects visual artifacts and perceptual descriptors, but cannot definitively prove out-of-context image reuse without comprehensive web reverse-search.")

        return limitations


prediction_explainer = PredictionExplainer()
