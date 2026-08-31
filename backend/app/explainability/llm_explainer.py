import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from backend.app.core.config import settings
from backend.app.core.logging_config import logger


class BaseLLMProvider(ABC):
    @abstractmethod
    async def synthesize_explanation(
        self,
        claim: str,
        verdict: str,
        confidence: float,
        key_reasons: List[str],
        supporting_evidence: List[Dict[str, Any]],
        contradicting_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        pass


class NullLLMProvider(BaseLLMProvider):
    """Offline default provider: Generates deterministic, research-grounded narrative synthesis without API calls."""
    async def synthesize_explanation(
        self,
        claim: str,
        verdict: str,
        confidence: float,
        key_reasons: List[str],
        supporting_evidence: List[Dict[str, Any]],
        contradicting_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        # Construct structured synthesis
        reasons_formatted = "\n".join([f"• {r}" for r in key_reasons])
        
        evidence_summary = ""
        if contradicting_evidence:
            top_c = contradicting_evidence[0]
            evidence_summary += f" Contradicting source ({top_c.get('source', 'Unknown')}): '{top_c.get('title', '')}'."
        if supporting_evidence:
            top_s = supporting_evidence[0]
            evidence_summary += f" Supporting source ({top_s.get('source', 'Unknown')}): '{top_s.get('title', '')}'."

        summary_text = (
            f"The system classified this content as **{verdict.replace('_', ' ')}** with {int(confidence*100)}% calibrated confidence. "
            f"Key factors driving this assessment include:\n{reasons_formatted}\n{evidence_summary}"
        )

        return {
            "provider": "NullProvider (Deterministic Local Synthesis)",
            "summary": summary_text,
            "claim_analysis": f"Evaluated core assertion: \"{claim[:180]}...\"",
            "evidence_synthesis": evidence_summary.strip() or "No direct matching evidence found in current database."
        }


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini LLM Provider with HTTP REST API + SDK fallbacks and resilient model cascading."""
    GEMINI_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.0-flash-lite",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._client = None

    def _init_client(self):
        if self._client is None and self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self._client = genai
                except Exception as e:
                    logger.info(f"SDK init skipped ({e}). Using direct HTTP REST API.")

    async def _generate_via_httpx(self, prompt: str) -> Optional[str]:
        """Direct REST API call to Gemini using httpx with multi-model fallback."""
        import httpx
        if not self.api_key:
            return None

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            for model in self.GEMINI_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                try:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        if "candidates" in data and len(data["candidates"]) > 0:
                            parts = data["candidates"][0].get("content", {}).get("parts", [])
                            text = "".join([p.get("text", "") for p in parts]).strip()
                            if text:
                                return text
                    else:
                        logger.debug(f"Gemini {model} returned {resp.status_code}: {resp.text[:100]}")
                except Exception as e:
                    logger.debug(f"Gemini {model} call failed: {e}")
        return None

    async def verify_claim_factuality(self, claim: str, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Query Gemini for real-time objective factual verification of a news assertion.
        Returns structured verdict, confidence, factual explanation, and verification signals.
        """
        if not self.api_key:
            return None

        full_text = f"Headline: {title}\nAssertion: {claim}" if title else f"Assertion: {claim}"
        prompt = f"""You are VeritasAI's real-time fact-checking verification intelligence.
Evaluate the factual accuracy and credibility of the following news assertion:
\"\"\"{full_text[:2000]}\"\"\"

Respond with STRICT JSON format only:
{{
  "verdict": "LIKELY_REAL" or "LIKELY_FAKE" or "UNCERTAIN",
  "confidence": <float between 0.50 and 0.99>,
  "explanation": "<2-3 sentence factual explanation citing consensus reality or debunking hoaxes>",
  "key_signals": ["<Signal 1>", "<Signal 2>"]
}}
Do NOT include markdown backticks or any other text outside the JSON object."""

        try:
            raw_response = await self._generate_via_httpx(prompt)
            if not raw_response:
                # Try SDK fallback
                self._init_client()
                if self._client:
                    for model in self.GEMINI_MODELS:
                        try:
                            if hasattr(self._client, "models"):
                                resp = self._client.models.generate_content(model=model, contents=prompt)
                                raw_response = resp.text.strip() if hasattr(resp, "text") else None
                            elif hasattr(self._client, "GenerativeModel"):
                                m = self._client.GenerativeModel(model)
                                resp = m.generate_content(prompt)
                                raw_response = resp.text.strip() if hasattr(resp, "text") else None
                            if raw_response:
                                break
                        except Exception:
                            continue

            if raw_response:
                import json
                cleaned = raw_response.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    cleaned = "\n".join(lines).strip()
                parsed = json.loads(cleaned)
                verdict = parsed.get("verdict", "").upper()
                if verdict in ("LIKELY_REAL", "LIKELY_FAKE", "UNCERTAIN"):
                    conf = float(parsed.get("confidence", 0.85))
                    conf = max(0.50, min(0.99, conf))
                    return {
                        "verdict": verdict,
                        "confidence": round(conf, 2),
                        "explanation": parsed.get("explanation", ""),
                        "key_signals": parsed.get("key_signals", [])
                    }
        except Exception as e:
            logger.warning(f"Real-time Gemini factuality verification error: {e}")
        return None

    async def synthesize_explanation(
        self,
        claim: str,
        verdict: str,
        confidence: float,
        key_reasons: List[str],
        supporting_evidence: List[Dict[str, Any]],
        contradicting_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not self.api_key:
            fallback = NullLLMProvider()
            return await fallback.synthesize_explanation(
                claim, verdict, confidence, key_reasons, supporting_evidence, contradicting_evidence
            )

        prompt = f"""You are an objective AI fact-checking researcher for VeritasAI.
Synthesize a concise verification explanation for this news content:
- Claim: {claim}
- Model Verdict: {verdict} (Confidence: {int(confidence*100)}%)
- Detected Signals: {', '.join(key_reasons)}
- Contradicting Evidence: {len(contradicting_evidence)} articles
- Supporting Evidence: {len(supporting_evidence)} articles

Provide a 3-sentence objective synthesis explaining why this verdict was reached, citing evidence stance clearly. Do not use inflammatory language."""

        try:
            summary = await self._generate_via_httpx(prompt)
            if summary:
                return {
                    "provider": "Google Gemini (Real-time AI Verification)",
                    "summary": summary,
                    "claim_analysis": f"Claim: {claim[:200]}",
                    "evidence_synthesis": f"{len(contradicting_evidence)} contradicting, {len(supporting_evidence)} supporting sources retrieved."
                }
        except Exception as e:
            logger.warning(f"Gemini REST API error: {e}")

        # SDK Client fallback
        self._init_client()
        if self._client:
            for model in self.GEMINI_MODELS:
                try:
                    if hasattr(self._client, "models"):
                        response = self._client.models.generate_content(
                            model=model,
                            contents=prompt,
                        )
                        summary = response.text.strip()
                    elif hasattr(self._client, "GenerativeModel"):
                        m = self._client.GenerativeModel(model)
                        response = m.generate_content(prompt)
                        summary = response.text.strip()
                    else:
                        summary = None

                    if summary:
                        return {
                            "provider": "Google Gemini (Real-time AI Verification)",
                            "summary": summary,
                            "claim_analysis": f"Claim: {claim[:200]}",
                            "evidence_synthesis": f"{len(contradicting_evidence)} contradicting, {len(supporting_evidence)} supporting sources retrieved."
                        }
                except Exception as e:
                    logger.debug(f"Gemini SDK generation error for {model}: {e}")

        fallback = NullLLMProvider()
        return await fallback.synthesize_explanation(
            claim, verdict, confidence, key_reasons, supporting_evidence, contradicting_evidence
        )


def get_llm_provider() -> BaseLLMProvider:
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if api_key:
        return GeminiLLMProvider(api_key=api_key)
    return NullLLMProvider()
