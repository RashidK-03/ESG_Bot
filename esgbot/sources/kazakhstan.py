import feedparser
import time
import requests
import re
from bs4 import BeautifulSoup

AIFC_RSS_URL = "https://aifc.kz/news/feed/"
AFSA_RSS_URL = "https://afsa.aifc.kz/news/feed/"
GFC_URL    = "https://gfc.aifc.kz/en/news"
GFC_DOMAIN = "https://gfc.aifc.kz"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

ESG_KEYWORDS = [
    "ESG", "sustainability", "green", "climate", "carbon",
    "disclosure", "taxonomy", "environment", "sustainable finance",
    "ISSB", "GRI", "TCFD", "reporting", "sustainable", "biodiversity",
    "framework", "regulation", "standard", "debenture", "emission"
]


def _is_esg(title: str, summary: str = "") -> bool:
    text = (title + " " + summary).lower()
    return any(k.lower() in text for k in ESG_KEYWORDS)


def _fetch_rss(source_name: str, rss_url: str, limit: int = 20) -> list[dict]:
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        print(f"[WARN] {source_name} RSS: {e}")
        return []

    results = []
    for entry in feed.entries[:limit]:
        title   = entry.get("title", "")
        summary = entry.get("summary", "")
        if not _is_esg(title, summary):
            continue
        results.append({
            "source":      source_name,
            "title":       title,
            "link":        entry.get("link", ""),
            "description": summary,
            "published":   entry.get("published", ""),
        })
    return results

def _fetch_gfc(pages: int = 2) -> list[dict]:
    results = []
    seen = set()

    for page_num in range(1, pages + 1):
        url = GFC_URL if page_num == 1 else f"{GFC_URL}?page={page_num}"

        # ── было: try/except без retry ──
        # ── стало: 2 попытки с паузой ──
        r = None
        for attempt in range(1, 3):
            try:
                r = requests.get(url, headers=HEADERS, timeout=20)
                r.raise_for_status()
                break
            except requests.RequestException as e:
                print(f"[WARN] GFC страница {page_num}, попытка {attempt}/2: {e}")
                if attempt < 2:
                    time.sleep(2)

        if r is None:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith(GFC_DOMAIN + "/news/"):
                continue
            if href in seen:
                continue

            title = ""
            for p in a.find_all("p"):
                text = p.get_text(strip=True)
                if text and len(text) > 15:
                    title = text
                    break

            if not title:
                title = a.get_text(strip=True)
                title = re.sub(r"\s+", " ", title).strip()

            if not title or len(title) < 15:
                continue

            date = ""
            parent = a.find_parent()
            if parent:
                date_match = re.search(
                    r"\d{1,2}\s+\w+\s+\d{4}",
                    parent.get_text()
                )
                if date_match:
                    date = date_match.group(0)

            paragraphs = [p.get_text(strip=True) for p in a.find_all("p")
                          if p.get_text(strip=True) and len(p.get_text(strip=True)) > 30]
            summary = paragraphs[1] if len(paragraphs) > 1 else ""

            seen.add(href)
            results.append({
                "source":      "Kazakhstan (GFC AIFC)",
                "title":       title,
                "link":        href,
                "description": summary[:300],
                "published":   date,
            })

    return results

def fetch_kz_updates() -> list[dict]:
    results = []
    results.extend(_fetch_rss("Kazakhstan (AIFC)", AIFC_RSS_URL))
    results.extend(_fetch_rss("Kazakhstan (AFSA)", AFSA_RSS_URL))
    results.extend(_fetch_gfc(pages=2))
    return results

