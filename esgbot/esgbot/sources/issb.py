import re
import asyncio
import time
import requests
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://www.ifrs.org/news-and-events/news/"
IFRS_DOMAIN = "https://www.ifrs.org"
KEYWORDS = ["ISSB", "IFRS S1", "IFRS S2", "sustainability", "climate", "SASB"]
NEWS_URL_PATTERN = "/news-and-events/news/20"

MONTHS = {
    "01": "January", "02": "February", "03": "March",
    "04": "April",   "05": "May",      "06": "June",
    "07": "July",    "08": "August",   "09": "September",
    "10": "October", "11": "November", "12": "December",
}

IASPLUS_URL = "https://www.iasplus.com/en/news"
IASPLUS_KEYWORDS = ["ISSB", "IFRS S1", "IFRS S2", "sustainability", "climate", "SASB"]

IASPLUS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
}

def _date_from_url(url: str) -> str | None:
    match = re.search(r"/news/(\d{4})/(\d{2})/", url)
    if match:
        year, month = match.group(1), match.group(2)
        return f"{MONTHS.get(month, month)} {year}"
    return None


def _extract_news_from_html(html) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if NEWS_URL_PATTERN not in href:
            continue
        if href.startswith("/"):
            href = IFRS_DOMAIN + href
            href = href.replace("/content/ifrs/home", "")
        if href in seen:
            continue

        title = a.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        seen.add(href)
        results.append({
            "source": "ISSB",
            "title": title,
            "link": href,
            "date": _date_from_url(href),
            "summary": "",
        })

    return results


async def _async_fetch_issb(limit: int, pages: int) -> list[dict]:
    results = []
    seen_links = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = await context.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4}", lambda r: r.abort())
        await page.route("**/{gtm,googletagmanager,rum.hlx,hotjar,adobe,analytics}**", lambda r: r.abort())

        for page_num in range(pages):
            url = BASE_URL if page_num == 0 else f"{BASE_URL}?page={page_num + 1}"

            for attempt in range(1, 4):
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(2)
                    break
                except Exception as e:
                    print(f"[WARN] Попытка {attempt}/3 для {url}: {e}")
                    await asyncio.sleep(3)
            else:
                print(f"[ERROR] Пропускаем страницу {page_num + 1}")
                continue

            items = _extract_news_from_html(await page.content())

            for item in items:
                if item["link"] in seen_links:
                    continue
                text = (item["title"] + " " + item["summary"]).lower()
                if not any(k.lower() in text for k in KEYWORDS):
                    continue
                seen_links.add(item["link"])
                results.append(item)

                if len(results) >= limit:
                    await browser.close()
                    return results

        await browser.close()

    return results[:limit]


def fetch_issb_news(limit=10, pages=2) -> list[dict]:
    """
    Пробует ifrs.org через Playwright.
    Если не получилось — использует iasplus.com как резерв.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, _async_fetch_issb(limit, pages))
            results = future.result()
    else:
        results = asyncio.run(_async_fetch_issb(limit, pages))

    # Если ifrs.org не ответил — используем iasplus.com
    if not results:
        print("[INFO] ifrs.org недоступен, переключаемся на iasplus.com")
        results = _fetch_issb_fallback(limit=limit)

    return results

def _fetch_issb_fallback(limit=10, pages=3) -> list[dict]:
    """Резервный парсер через iasplus.com — работает без Playwright."""
    results = []
    session = requests.Session()
    session.headers.update(IASPLUS_HEADERS)

    for page in range(pages):
        url = f"{IASPLUS_URL}?b_start:int={page * 20}"
        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[WARN] iasplus fallback страница {page + 1}: {e}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        for article in soup.select(".listingSummary"):
            title_el   = article.select_one("h2 a")
            date_el    = article.select_one(".listingDate")
            summary_el = article.select_one(".listingSummaryDescription")

            if not title_el:
                continue

            title   = title_el.get_text(strip=True)
            summary = summary_el.get_text(strip=True) if summary_el else ""

            if not any(k.lower() in (title + summary).lower() for k in IASPLUS_KEYWORDS):
                continue

            link = title_el["href"]
            if link.startswith("/"):
                link = "https://www.iasplus.com" + link

            results.append({
                "source":      "ISSB",
                "title":       title,
                "link":        link,
                "date":        date_el.get_text(strip=True) if date_el else "",
                "summary":     summary,
                "description": summary,
            })

            if len(results) >= limit:
                return results

    return results