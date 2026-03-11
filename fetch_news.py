"""
fetch_news.py — Step 1: Extract news articles from NewsAPI
Saves raw JSON to data/raw/ folder (the "bronze" data layer).
"""

import requests
import json
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "your_key_here")
BASE_URL = "https://newsapi.org/v2/everything"


def fetch_news(query: str = "technology", page_size: int = 100) -> list:
    """
    Fetches news articles from NewsAPI for a given topic.
    Returns a list of article dictionaries.
    Free tier: 100 requests/day, 100 articles per request.
    """
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "q": query,
        "from": yesterday,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "language": "en",
        "apiKey": NEWS_API_KEY,
    }

    log.info(f"Fetching '{query}' news from NewsAPI...")

    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error(f"NewsAPI request failed: {e}")
        raise

    data = response.json()

    if data.get("status") != "ok":
        raise ValueError(f"NewsAPI returned error: {data.get('message')}")

    articles = data.get("articles", [])
    log.info(f"Fetched {len(articles)} articles")

    # ── Save raw JSON to data/raw/ (bronze layer) ─────────────
    os.makedirs("data/raw", exist_ok=True)
    filename = f"data/raw/news_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(articles, f, indent=2)

    log.info(f"Raw articles saved → {filename}")
    return articles


if __name__ == "__main__":
    fetch_news(query="artificial intelligence")
