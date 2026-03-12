from sources.gri import fetch_gri_news

def test():
    news = fetch_gri_news(limit=5, pages=2)
    print("News count:", len(news))
    for item in news:
        print(item["title"])
        print(item["date"])
        print(item["link"])
        print(item["summary"])
        print("-" * 60)

if __name__ == "__main__":
    test()