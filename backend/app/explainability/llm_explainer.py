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
    """Google Gemini LLM Provider with HTTP REST API + SDK fallbacks."""
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
                    logger.info(f"SDK init skipped ({e}). Using direct HTTP API for Gemini 2.5 Flash.")

    async def _generate_via_httpx(self, prompt: str) -> Optional[str]:
        """Direct REST API call to Gemini 2.5 Flash using httpx (zero extra dependencies)."""
        import httpx
        if not self.api_key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    parts = data["candidates"][0].get("content", {}).get("parts", [])
                    text = "".join([p.get("text", "") for p in parts]).strip()
                    if text:
                        return text
            else:
                logger.warning(f"Gemini REST API returned status {resp.status_code}: {resp.text[:200]}")
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

        # 1. Try Direct REST API
        try:
            summary = await self._generate_via_httpx(prompt)
            if summary:
                return {
                    "provider": "Gemini 2.5 Flash (Google AI)",
                    "summary": summary,
                    "claim_analysis": f"Claim: {claim[:200]}",
                    "evidence_synthesis": f"{len(contradicting_evidence)} contradicting, {len(supporting_evidence)} supporting sources retrieved."
                }
        except Exception as e:
            logger.warning(f"Gemini REST API error: {e}")

        # 2. Try SDK Client
        self._init_client()
        if self._client:
            try:
                if hasattr(self._client, "models"):
                    response = self._client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                    )
                    summary = response.text.strip()
                elif hasattr(self._client, "GenerativeModel"):
                    m = self._client.GenerativeModel("gemini-2.5-flash")
                    response = m.generate_content(prompt)
                    summary = response.text.strip()
                else:
                    summary = None

                if summary:
                    return {
                        "provider": "Gemini 2.5 Flash (Google AI)",
                        "summary": summary,
                        "claim_analysis": f"Claim: {claim[:200]}",
                        "evidence_synthesis": f"{len(contradicting_evidence)} contradicting, {len(supporting_evidence)} supporting sources retrieved."
                    }
            except Exception as e:
                logger.warning(f"Gemini SDK generation error ({e}). Using offline synthesis.")

        fallback = NullLLMProvider()
        return await fallback.synthesize_explanation(
            claim, verdict, confidence, key_reasons, supporting_evidence, contradicting_evidence
        )


def get_llm_provider() -> BaseLLMProvider:
    if (settings.LLM_PROVIDER.lower() == "gemini" or settings.GEMINI_API_KEY) and settings.GEMINI_API_KEY:
        return GeminiLLMProvider()
    return NullLLMProvider()
