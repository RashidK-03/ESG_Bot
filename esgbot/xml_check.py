import requests
from bs4 import BeautifulSoup

URL = "https://www.ifrs.org/news-and-events/news/"

def fetch_ifrs_news():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []

    for item in soup.select(".listing__item"):  # примерный CSS‑селектор
        title = item.select_one(".listing__title").get_text(strip=True)
        link = "https://www.ifrs.org" + item.select_one("a")["href"]
        date = item.select_one(".listing__date").get_text(strip=True)

        news_items.append({
            "title": title,
            "link": link,
            "date": date
        })

    return news_items