from sources.eu_commission import fetch_eu_updates
from sources.gri import fetch_gri_news
from sources.issb import fetch_issb_news
from sources.kazakhstan import fetch_kz_updates
from database import save_update

ESG_KEYWORDS = [
    "sustainability", "climate", "environment", "taxonomy",
    "green", "ESG", "sustainable finance", "emissions",
    "energy", "water", "biodiversity", "carbon",
    "ISSB", "GRI", "IFRS S1", "IFRS S2", "CSRD", "TCFD"
]


def is_esg_related(title, description):
    text = (title + " " + description).lower()
    return any(keyword.lower() in text for keyword in ESG_KEYWORDS)


def check_all_sources(chat_id: str) -> list[dict]:   # ← добавили chat_id
    all_updates = []

    raw_sources = [
        fetch_eu_updates(),
        fetch_gri_news(limit=10, pages=2),
        fetch_issb_news(limit=10, pages=2),
        fetch_kz_updates(),
    ]

    for source_updates in raw_sources:
        for item in source_updates:
            title       = item.get("title", "")
            description = item.get("description") or item.get("summary", "")
            link        = item.get("link", "")

            if not is_esg_related(title, description):
                continue

            is_new = save_update(
                chat_id=chat_id,        # ← передаём chat_id
                source=item.get("source", ""),
                title=title,
                link=link,
                published=item.get("date") or item.get("published", ""),
            )

            if is_new:
                all_updates.append({
                    "source":      item.get("source", ""),
                    "title":       title,
                    "link":        link,
                    "description": description,
                    "published":   item.get("date") or item.get("published", ""),
                })

    return all_updates