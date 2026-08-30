"""
VeritasAI Real-Time Search Service — Free Sources Edition
===========================================================
100% free, no API keys, no rate limits, no credit costs.

Source stack (ranked by accuracy for news fact-checking):
  1. Bing News RSS       — Real-time breaking news (no key, no limits)
  2. Wikipedia REST      — Encyclopedic facts, entity status, biographies
  3. DuckDuckGo Instant  — Topic knowledge graph summaries
  4. Wikipedia Search    — Broader semantic article search

Why this is accurate:
  - Bing News RSS aggregates 1000s of news sources in real time
  - Wikipedia REST provides the most up-to-date encyclopedic facts
  - Multi-source corroboration reduces single-source bias
  - Stance evaluation uses both keyword AND semantic pattern analysis
"""
import re
import json
import html
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple
from backend.app.core.logging_config import logger


# ---------------------------------------------------------------------------
# Domain credibility registry — the more authoritative the domain, the
# more weight its stance carries in evidence scoring.
# ---------------------------------------------------------------------------
DOMAIN_CREDIBILITY: Dict[str, float] = {
    # Tier 1 — International wire services / govt / scientific
    "reuters.com": 0.97, "apnews.com": 0.97,
    "who.int": 0.99, "cdc.gov": 0.99, "nih.gov": 0.98,
    "nature.com": 0.98, "sciencemag.org": 0.98,
    "pbs.org": 0.93, "npr.org": 0.93,

    # Tier 2 — Major broadcasters & newspapers
    "bbc.com": 0.95, "bbc.co.uk": 0.95,
    "theguardian.com": 0.92, "nytimes.com": 0.91,
    "washingtonpost.com": 0.91, "bloomberg.com": 0.92,
    "ft.com": 0.92, "economist.com": 0.92,
    "wsj.com": 0.91, "time.com": 0.86,
    "nbcnews.com": 0.86, "cbsnews.com": 0.87,
    "abcnews.go.com": 0.87, "cnn.com": 0.84,
    "usatoday.com": 0.84, "newsweek.com": 0.81,
    "aljazeera.com": 0.87, "dw.com": 0.91,
    "abc.net.au": 0.90, "sky.com": 0.85,
    "independent.co.uk": 0.85, "telegraph.co.uk": 0.84,
    "forbes.com": 0.83, "businessinsider.com": 0.80,
    "techcrunch.com": 0.84, "wired.com": 0.85,

    # Tier 3 — Fact checkers
    "snopes.com": 0.96, "politifact.com": 0.96,
    "factcheck.org": 0.95, "fullfact.org": 0.95,
    "leadstories.com": 0.88, "checkyourfact.com": 0.85,
    "boomlive.in": 0.86, "factly.in": 0.86,
    "altnews.in": 0.87, "vishvasnews.com": 0.82,

    # Tier 4 — Indian news
    "thehindu.com": 0.88, "ndtv.com": 0.85,
    "hindustantimes.com": 0.84, "timesofindia.com": 0.82,
    "indiatoday.in": 0.83, "livemint.com": 0.86,
    "businessstandard.com": 0.86, "economictimes.indiatimes.com": 0.84,
    "financialexpress.com": 0.84, "scroll.in": 0.84,
    "thewire.in": 0.83, "firstpost.com": 0.80,
    "news18.com": 0.79, "zeenews.india.com": 0.76,
    "theprint.in": 0.83, "outlookindia.com": 0.82,

    # Tier 5 — Encyclopedia
    "wikipedia.org": 0.88,
    "en.wikipedia.org": 0.88,

    # Lower credibility
    "foxnews.com": 0.71, "mirror.co.uk": 0.70,
    "dailymail.co.uk": 0.65, "nypost.com": 0.68,
    "msn.com": 0.76, "yahoo.com": 0.74,
}

# Signals for stance classification
DEBUNK_SIGNALS = frozenset({
    "debunked", "false", "hoax", "misinformation", "disproven",
    "fact-check", "fact check", "no evidence", "conspiracy theory",
    "fake news", "unverified", "misleading", "fabricated", "viral fake",
    "false claim", "doctored", "manipulated", "out of context",
    "missing context", "satire", "parody", "not true", "incorrect",
})
CONFIRM_SIGNALS = frozenset({
    "confirmed", "verified", "official", "announced", "published",
    "evidence shows", "data shows", "study found", "research shows",
    "according to", "scientists say", "researchers say", "report shows",
    "ministry announced", "government announced", "health ministry",
    "court ruled", "police confirmed", "officially", "authenticated",
})
ALIVE_SIGNALS = frozenset({
    "alive", "in office", "serving", "announced today", "said today",
    "met with", "signed", "declared", "inaugurated", "spoke", "tweeted",
    "posted", "active", "continues to", "remains", "leads", "heads",
    "visited", "inaugurated", "addressed", "released statement",
    "held meeting", "presides", "administers", "governing",
})
DEATH_CLAIM_WORDS = frozenset({
    "died", "dead", "passed away", "killed", "assassinated",
    "death", "murdered", "shot dead", "hanged", "executed",
})
CURE_CLAIM_WORDS = frozenset({
    "cures cancer", "cures all", "miracle cure", "100% effective",
    "destroys cancer", "eliminates cancer", "treats all disease",
    "single remedy", "cures diabetes", "cures aids",
})


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _safe_get(url: str, timeout: float = 6.0, extra_headers: Optional[Dict] = None) -> Optional[bytes]:
    """Safe HTTP GET — returns bytes or None on any error."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        logger.debug(f"[Search] HTTP error {url[:70]}: {e}")
        return None


def _domain_from_url(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.replace("www.", "").lower()
    except Exception:
        return ""


def get_credibility(url: str) -> float:
    domain = _domain_from_url(url)
    if domain in DOMAIN_CREDIBILITY:
        return DOMAIN_CREDIBILITY[domain]
    for k, v in DOMAIN_CREDIBILITY.items():
        if domain.endswith("." + k):
            return v
    return 0.72


# ---------------------------------------------------------------------------
# Query extraction
# ---------------------------------------------------------------------------

def extract_search_query(claim: str) -> str:
    """
    Extract the best search query from a claim text.
    Priority: Named entities > Key nouns > First meaningful words.
    Strips clickbait/emotional words that would bias search results.
    """
    # Remove URLs and special chars
    text = re.sub(r'https?://\S+', '', claim)
    text = re.sub(r'[!?*@#$%^&(){}\[\]|\\~`=+<>]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    STOPWORDS = frozenset({
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "this", "that", "these", "those", "with", "from", "into", "through",
        "and", "but", "or", "if", "as", "at", "by", "for", "in", "of", "on",
        "to", "up", "can", "will", "just", "should", "now", "have", "has",
        "had", "may", "says", "said", "also", "new", "more", "no", "not",
        "do", "does", "did", "about", "so", "when", "where", "who", "which",
        "how", "what", "its", "it", "he", "she", "we", "they", "them",
        "their", "his", "her", "my", "your", "our", "would", "could",
        "should", "might", "must", "shall", "want", "need", "make", "made",
        "come", "go", "get", "know", "think", "see", "look", "use", "find",
        "give", "tell", "work", "call", "try", "ask", "seem", "feel", "keep",
        "let", "begin", "show", "hear", "play", "run", "move", "live",
        "believe", "hold", "bring", "write", "provide", "sit", "stand",
    })
    EMOTIONAL_NOISE = frozenset({
        "shocking", "bombshell", "secret", "exposed", "breaking", "urgent",
        "truth", "hidden", "revealed", "amazing", "incredible", "unbelievable",
        "must", "share", "watch", "read", "click", "viral", "wow",
    })

    words = text.split()

    # Extract proper nouns (capitalized, 2+ chars, not acronyms or sentence-start)
    proper = []
    for i, w in enumerate(words):
        clean = re.sub(r"[^a-zA-Z0-9'\-]", '', w)
        if (len(clean) >= 2
                and clean[0].isupper()
                and not clean.isupper()
                and clean.lower() not in STOPWORDS
                and clean.lower() not in EMOTIONAL_NOISE):
            proper.append(clean)

    if len(proper) >= 2:
        return " ".join(proper[:5])[:110]

    # Fallback: meaningful content words
    content = []
    for w in words:
        clean = re.sub(r"[^a-zA-Z0-9'\-]", '', w)
        if (len(clean) >= 4
                and clean.lower() not in STOPWORDS
                and clean.lower() not in EMOTIONAL_NOISE):
            content.append(clean)
    if content:
        return " ".join(content[:6])[:110]

    return " ".join(words[:6])[:80]


# ---------------------------------------------------------------------------
# Stance evaluation
# ---------------------------------------------------------------------------

def evaluate_stance(claim: str, title: str, body: str) -> Tuple[str, float]:
    """
    Classify whether this evidence SUPPORTS, CONTRADICTS, or is CONTEXTUAL
    relative to the claim. Returns (label, confidence).
    """
    claim_l = claim.lower()
    ev_l = (title + " " + body).lower()

    # ── Death claim vs alive evidence ──────────────────────────────────────
    is_death_claim = any(w in claim_l for w in DEATH_CLAIM_WORDS)
    ev_words = set(re.findall(r'\b\w+\b', ev_l))
    is_alive_ev = bool(ALIVE_SIGNALS & ev_words)
    if is_death_claim and is_alive_ev:
        return "Contradicting", 0.92

    # ── Miracle cure claim vs medical evidence ─────────────────────────────
    is_cure_claim = any(phrase in claim_l for phrase in CURE_CLAIM_WORDS)
    if is_cure_claim:
        debunk_hits = sum(1 for w in DEBUNK_SIGNALS if w in ev_l)
        if debunk_hits >= 1 or any(p in ev_l for p in ["no food cures", "no single", "does not cure", "no evidence"]):
            return "Contradicting", 0.88

    # ── Fact-checking / debunking article ─────────────────────────────────
    debunk_hits = sum(1 for w in DEBUNK_SIGNALS if w in ev_l)
    if debunk_hits >= 2:
        return "Contradicting", 0.80
    if debunk_hits == 1 and any(w in ev_l for w in ["claim", "article", "post", "video", "report"]):
        return "Contradicting", 0.68

    # ── Confirming / corroborating article ────────────────────────────────
    confirm_hits = sum(1 for w in CONFIRM_SIGNALS if w in ev_l)
    if confirm_hits >= 3:
        return "Supporting", 0.78
    if confirm_hits >= 1:
        return "Supporting", 0.62

    # ── Query-to-evidence word overlap (topic relevance) ──────────────────
    claim_tokens = set(re.findall(r'\b\w{4,}\b', claim_l))
    ev_tokens = set(re.findall(r'\b\w{4,}\b', ev_l))
    overlap_ratio = len(claim_tokens & ev_tokens) / max(len(claim_tokens), 1)
    if overlap_ratio > 0.5:
        return "Supporting", 0.52

    return "Contextual", 0.38


def compute_relevance(query: str, title: str, body: str) -> float:
    """Word-overlap relevance score 0.0–1.0."""
    q_words = set(re.findall(r'\b\w{4,}\b', query.lower()))
    d_words = set(re.findall(r'\b\w{4,}\b', (title + " " + body).lower()))
    if not q_words:
        return 0.38
    overlap = len(q_words & d_words)
    raw = (overlap / len(q_words)) * 1.4 + 0.22
    return round(min(0.95, raw), 4)


# ---------------------------------------------------------------------------
# Source 1: Bing News RSS — PRIMARY real-time source
# ---------------------------------------------------------------------------

def _parse_rss_tag(xml: str, tag: str) -> str:
    m = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', xml, re.DOTALL | re.IGNORECASE)
    if m:
        val = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', m.group(1))
        return html.unescape(re.sub(r'<[^>]+>', '', val).strip())
    return ""


def search_bing_news(query: str, top_n: int = 8) -> List[Dict]:
    """
    Fetch real-time news from Bing News RSS.
    No key required. Updates continuously. Covers global + Indian sources.
    """
    results = []
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://www.bing.com/news/search?q={encoded}&format=rss&count={top_n}"
        raw = _safe_get(url, timeout=7.0)
        if not raw:
            return results

        content = raw.decode("utf-8", errors="ignore")
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)

        for xml in items[:top_n]:
            title = _parse_rss_tag(xml, "title")
            desc = _parse_rss_tag(xml, "description")
            link = _parse_rss_tag(xml, "link")
            pub = _parse_rss_tag(xml, "pubDate")
            src = _parse_rss_tag(xml, "source") or _domain_from_url(link)

            if not title or not link:
                continue

            # Bing sometimes double-encodes or wraps links
            if not link.startswith("http"):
                link_m = re.search(r'https?://[^\s<"]+', xml)
                if link_m:
                    link = link_m.group()

            domain = _domain_from_url(link)
            text = desc or title
            results.append({
                "title": title[:200],
                "text": text[:600],
                "source": src,
                "url": link,
                "publication_date": pub[:30] if pub else "Recent",
                "domain": domain,
                "raw": title + " " + text,
                "_src": "bing_rss",
            })

        logger.info(f"[BingRSS] ✅ {len(results)} results | query: '{query[:55]}'")
    except Exception as e:
        logger.warning(f"[BingRSS] Error: {e}")
    return results


def search_google_news_rss(query: str, top_n: int = 6) -> List[Dict]:
    """
    Fetch from Google News RSS as secondary real-time source.
    """
    results = []
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        raw = _safe_get(url, timeout=7.0)
        if not raw:
            return results

        content = raw.decode("utf-8", errors="ignore")
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)

        for xml in items[:top_n]:
            title = _parse_rss_tag(xml, "title")
            desc = _parse_rss_tag(xml, "description")
            link = _parse_rss_tag(xml, "link")
            pub = _parse_rss_tag(xml, "pubDate")
            src = _parse_rss_tag(xml, "source") or "Google News"

            if not title or not link:
                continue

            # Google News links are redirect URLs - extract source from title
            # Title format: "Article Title - Source Name"
            source_name = src
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0].strip()
                source_name = parts[1].strip()

            domain = _domain_from_url(link)
            text = desc or title
            results.append({
                "title": title[:200],
                "text": text[:600],
                "source": source_name,
                "url": link,
                "publication_date": pub[:30] if pub else "Recent",
                "domain": domain or "google.com",
                "raw": title + " " + text,
                "_src": "google_news",
            })

        logger.info(f"[GoogleNews] ✅ {len(results)} results | query: '{query[:55]}'")
    except Exception as e:
        logger.warning(f"[GoogleNews] Error: {e}")
    return results


# ---------------------------------------------------------------------------
# Source 2: Wikipedia REST API — facts, entities, biographies
# ---------------------------------------------------------------------------

def search_wikipedia(query: str, top_n: int = 3) -> List[Dict]:
    """
    Fetch encyclopedic summaries for entities in the claim.
    The Wikipedia REST API gives the most accurate, up-to-date factual basis.
    """
    results = []
    try:
        # Step 1: Find matching articles
        search_url = (
            f"https://en.wikipedia.org/w/api.php"
            f"?action=query&list=search&srsearch={urllib.parse.quote(query)}"
            f"&srlimit={top_n}&utf8=&format=json&srprop=snippet|titlesnippet"
        )
        raw = _safe_get(search_url, timeout=5.0)
        if not raw:
            return results

        data = json.loads(raw.decode("utf-8"))
        items = data.get("query", {}).get("search", [])

        for item in items[:top_n]:
            wiki_title = item.get("title", "")
            snippet = html.unescape(re.sub(r'<[^>]+>', '', item.get("snippet", "")))
            if len(snippet) < 15:
                continue

            # Step 2: Fetch full summary (much richer than snippet)
            encoded_title = urllib.parse.quote(wiki_title.replace(" ", "_"))
            sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
            sum_raw = _safe_get(sum_url, timeout=5.0)
            extract = snippet

            if sum_raw:
                try:
                    sd = json.loads(sum_raw.decode("utf-8"))
                    full_extract = sd.get("extract", "")
                    # Use up to 600 chars — enough for stance evaluation
                    if full_extract and len(full_extract) > 40:
                        extract = full_extract[:600]
                except Exception:
                    pass

            wiki_url = f"https://en.wikipedia.org/wiki/{encoded_title}"
            results.append({
                "title": f"Wikipedia: {wiki_title}",
                "text": extract[:600],
                "source": "Wikipedia — Encyclopedic Reference",
                "url": wiki_url,
                "publication_date": "Current",
                "domain": "wikipedia.org",
                "raw": wiki_title + " " + extract,
                "_src": "wikipedia",
            })

        logger.info(f"[Wikipedia] ✅ {len(results)} results | query: '{query[:55]}'")
    except Exception as e:
        logger.warning(f"[Wikipedia] Error: {e}")
    return results


# ---------------------------------------------------------------------------
# Source 3: DuckDuckGo Instant Answer API
# ---------------------------------------------------------------------------

def search_duckduckgo(query: str) -> List[Dict]:
    """
    Fetch DuckDuckGo Instant Answer knowledge graph summaries.
    Excellent for well-known entities (politicians, celebrities, events).
    """
    results = []
    try:
        url = (
            f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}"
            f"&format=json&no_html=1&skip_disambig=1&kl=us-en"
        )
        raw = _safe_get(url, timeout=5.0)
        if not raw:
            return results

        data = json.loads(raw.decode("utf-8"))
        abstract = data.get("AbstractText", "").strip()
        abstract_url = data.get("AbstractURL", "")
        abstract_src = data.get("AbstractSource", "DuckDuckGo")
        heading = data.get("Heading", "").strip()

        if abstract and len(abstract) > 50:
            domain = _domain_from_url(abstract_url) if abstract_url else "duckduckgo.com"
            results.append({
                "title": f"Knowledge: {heading or query}",
                "text": abstract[:600],
                "source": abstract_src,
                "url": abstract_url or f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                "publication_date": "Current",
                "domain": domain,
                "raw": (heading or query) + " " + abstract,
                "_src": "duckduckgo",
            })

        # Related topics (additional facts)
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
                t = topic["Text"].strip()
                if len(t) > 40:
                    results.append({
                        "title": t[:100],
                        "text": t[:400],
                        "source": "DuckDuckGo Knowledge Graph",
                        "url": topic["FirstURL"],
                        "publication_date": "Current",
                        "domain": "duckduckgo.com",
                        "raw": t,
                        "_src": "duckduckgo",
                    })

        logger.info(f"[DDG] ✅ {len(results)} results | query: '{query[:55]}'")
    except Exception as e:
        logger.warning(f"[DDG] Error: {e}")
    return results


# ---------------------------------------------------------------------------
# Master orchestrator
# ---------------------------------------------------------------------------

def fetch_live_evidence(claim_text: str, top_k: int = 8) -> List[Dict[str, Any]]:
    """
    Fetch and rank real-time evidence from all free sources.
    Returns EvidenceItem-compatible dicts, sorted by relevance + stance quality.
    """
    query = extract_search_query(claim_text)
    logger.info(f"[LiveSearch] 🔍 Query: '{query}' | Claim: '{claim_text[:70]}'")

    raw: List[Dict] = []

    # ── 1. Bing News RSS (real-time news) ─────────────────────────────────
    bing = search_bing_news(query, top_n=8)
    raw.extend(bing)

    # ── 2. Google News RSS (additional real-time news) ────────────────────
    gnews = search_google_news_rss(query, top_n=6)
    raw.extend(gnews)

    # ── 3. Wikipedia (entity facts / biographies) ─────────────────────────
    wiki = search_wikipedia(query, top_n=3)
    raw.extend(wiki)

    # ── 4. DuckDuckGo (knowledge graph) ───────────────────────────────────
    ddg = search_duckduckgo(query)
    raw.extend(ddg)

    logger.info(f"[LiveSearch] Total raw items before dedup: {len(raw)}")

    if not raw:
        logger.warning(f"[LiveSearch] ⚠️ All sources empty for: '{query}'")
        return []

    # ── Score + deduplicate ────────────────────────────────────────────────
    seen: set = set()
    scored: List[Dict[str, Any]] = []

    for idx, r in enumerate(raw):
        title = (r.get("title") or "").strip()
        if not title:
            continue
        key = re.sub(r'\W+', '', title[:50].lower())
        if key in seen:
            continue
        seen.add(key)

        url = r.get("url", "")
        domain = r.get("domain", "") or _domain_from_url(url)
        raw_text = r.get("raw", r.get("text", ""))
        cred = DOMAIN_CREDIBILITY.get(domain, get_credibility(url))
        relevance = compute_relevance(query, title, raw_text)
        stance, conf = evaluate_stance(claim_text, title, raw_text)

        # Source-type boosts for recency / authority
        src_type = r.get("_src", "")
        if src_type in ("bing_rss", "google_news"):
            relevance = min(0.96, relevance + 0.07)  # recency bonus
        elif src_type == "wikipedia":
            cred = min(0.92, cred + 0.04)  # encyclopedia authority bonus

        adjusted = round(relevance * cred, 4)

        scored.append({
            "id": 10000 + idx,
            "title": title[:200],
            "text": r.get("text", "")[:600],
            "source": r.get("source", domain),
            "url": url,
            "publication_date": r.get("publication_date", "Recent"),
            "domain": domain,
            "similarity": round(relevance, 4),
            "credibility_score": round(cred, 4),
            "adjusted_score": adjusted,
            "stance": stance,
            "category": "Live",
            "_is_live": True,
            "_source_type": src_type,
        })

    # Sort: definitive stances first (contradicting/supporting), then by score
    scored.sort(key=lambda e: (
        0 if e["stance"] in ("Contradicting", "Supporting") else 1,
        -e["adjusted_score"]
    ))

    final = scored[:top_k]
    logger.info(
        f"[LiveSearch] ✅ Returning {len(final)} items | "
        f"Stances: {[e['stance'] for e in final]}"
    )
    return final
