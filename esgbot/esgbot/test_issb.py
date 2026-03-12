from sources.issb import fetch_issb_news

def test():
    news = fetch_issb_news(limit=5, pages=5)
    print("News count:", len(news))

    if not news:
        print(
            "\n⚠️  Ничего не найдено. Возможные причины:\n"
            "  1. ifrs.org заблокировал запрос (попробуйте VPN)\n"
            "  2. Сайт изменил HTML-структуру\n"
            "  3. Страница требует JavaScript (нужен playwright)\n"
            "\nДля диагностики выполните:\n"
            "  python -c \"from sources.issb import _debug; _debug()\""
        )
        return

    for item in news:
        print(item["title"])
        print(item["date"])
        print(item["link"])
        print(item["summary"])
        print("-" * 60)

if __name__ == "__main__":
    test()