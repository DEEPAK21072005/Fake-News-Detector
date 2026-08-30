import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from backend.app.core.security import is_safe_url, sanitize_text
from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.core.error_handlers import VeritasException


def scrape_article_from_url(url: str) -> Dict[str, Any]:
    """
    Safely retrieves and parses article headline, body, and metadata from a URL.
    Enforces SSRF protection, strict timeouts, and size limits.
    """
    is_safe, error_msg = is_safe_url(url)
    if not is_safe:
        raise VeritasException(
            message=f"URL safety validation failed: {error_msg}",
            status_code=400,
            suggestion="Please provide a valid public HTTP/HTTPS news article URL or paste the text directly."
        )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 VeritasAI-Research/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=settings.SCRAPER_TIMEOUT_SECONDS,
            allow_redirects=True,
            stream=True
        )
        response.raise_for_status()

        # Check content length
        content_bytes = response.raw.read(settings.MAX_SCRAPED_CHARS * 4, decode_content=True)
        html = content_bytes.decode("utf-8", errors="ignore")

        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts, styles, nav, footer, ads
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "form"]):
            element.decompose()

        # Extract Title
        title = ""
        if soup.find("h1"):
            title = soup.find("h1").get_text().strip()
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title").get("content", "").strip()
        elif soup.title:
            title = soup.title.get_text().strip()

        # Extract Body Paragraphs
        paragraphs = soup.find_all("p")
        body_text_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30]
        body_text = "\n\n".join(body_text_parts)

        if not body_text:
            body_text = soup.get_text(separator=" ", strip=True)

        body_text = sanitize_text(body_text, max_chars=settings.MAX_SCRAPED_CHARS)

        if len(body_text) < 50:
            raise VeritasException(
                message="Unable to extract meaningful article text from this URL.",
                status_code=422,
                suggestion="The page may be paywalled, require JavaScript rendering, or block automated retrieval. Please copy and paste the article text directly."
            )

        # Extract Domain
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")

        # Extract Author / Date if available
        author = ""
        meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
        if meta_author:
            author = meta_author.get("content", "")

        date_published = ""
        meta_date = soup.find("meta", property="article:published_time") or soup.find("meta", attrs={"name": "pubdate"})
        if meta_date:
            date_published = meta_date.get("content", "")

        return {
            "title": title[:300],
            "text": body_text,
            "domain": domain,
            "url": url,
            "author": author[:100],
            "publication_date": date_published[:50],
            "word_count": len(body_text.split())
        }

    except requests.exceptions.RequestException as e:
        logger.warning(f"URL scraping failed for {url}: {e}")
        raise VeritasException(
            message="Unable to connect to the provided URL.",
            status_code=400,
            details=str(e),
            suggestion="Verify the URL is accessible and not blocking requests, or paste the article text into the editor."
        )
