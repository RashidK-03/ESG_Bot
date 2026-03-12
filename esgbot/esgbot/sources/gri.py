import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.globalreporting.org/news/news-center/"
GRI_DOMAIN = "https://www.globalreporting.org"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_gri_news(limit=10, pages=5):
    results = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for page_num in range(1, pages + 1):
        params = {"page": page_num} if page_num > 1 else {}

        try:
            response = session.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[WARN] Страница {page_num}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        for h4 in soup.find_all("h4"):
            link_el = h4.find("a", href=re.compile(r"^/news/news-center/[^/]+/$"))
            if not link_el:
                continue

            href = GRI_DOMAIN + link_el["href"]
            title = link_el.get_text(strip=True)
            if not title:
                continue

            summary = ""
            date = None


            for node in h4.next_siblings:
                if hasattr(node, "name") and node.name == "h4":
                    break

                if node.name == "p":
                    text = node.get_text(strip=True)
                    if text and not summary:
                        summary = text[:200]

                elif node.name == "div":
                    span = node.find("span", class_="list-card__date")
                    if span:
                        date = span.get_text(strip=True)

            results.append({
                "source": "GRI",
                "title": title,
                "link": href,
                "date": date,
                "summary": summary,
            })

            if len(results) >= limit:
                return results

    return results