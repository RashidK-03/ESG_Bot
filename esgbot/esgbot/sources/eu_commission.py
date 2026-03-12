from sources.rss_source import fetch_rss_updates
EU_RSS_URL = "https://ec.europa.eu/commission/presscorner/api/rss"
def fetch_eu_updates(): return fetch_rss_updates("EU Commission", EU_RSS_URL)
