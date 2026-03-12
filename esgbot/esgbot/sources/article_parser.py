import requests
from bs4 import BeautifulSoup

def extract_article_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        print("Status code:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, "lxml")

    article_text = ""


    content_div = soup.find("div", class_="ecl-container")

    if content_div:
        paragraphs = content_div.find_all("p")

        for p in paragraphs:
            text = p.get_text().strip()
            if text:
                article_text += text + "\n"

    return article_text.strip()[:4000] if article_text else None