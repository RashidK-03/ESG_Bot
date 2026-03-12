import feedparser

def fetch_rss_updates(source_name, rss_url):
    feed = feedparser.parse(rss_url)
    updates = []

    for entry in feed.entries:
        updates.append({
            "source": source_name,
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "description": entry.get("summary", "") or entry.get("description", ""),
            "published": entry.get("published", ""),
        })

    return updates