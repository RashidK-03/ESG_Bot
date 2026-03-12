from sources.kazakhstan import fetch_kz_updates

def test():
    news = fetch_kz_updates()
    print(f"Всего новостей: {len(news)}\n")
    for item in news:
        print(f"[{item['source']}]")
        print(f"  {item['title']}")
        print(f"  {item['published'] or 'дата не указана'}")
        print(f"  {item['link']}")
        print()

if __name__ == "__main__":
    test()