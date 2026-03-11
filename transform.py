"""
transform.py — Step 2: Clean and validate raw news articles.
Removes duplicates, strips HTML, normalises dates (silver layer).
"""

import pandas as pd
import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def strip_html(text: str) -> str:
    """Remove HTML tags from a string."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def transform(articles: list) -> pd.DataFrame:
    """
    Cleans a list of raw article dicts.
    Returns a clean Pandas DataFrame ready for AI analysis.
    """
    if not articles:
        log.warning("No articles to transform")
        return pd.DataFrame()

    df = pd.DataFrame(articles)
    original_count = len(df)

    # ── 1. Select only the columns we need ────────────────────
    cols = ["title", "description", "source", "url", "publishedAt"]
    df = df[[c for c in cols if c in df.columns]]

    # ── 2. Flatten nested 'source' column ─────────────────────
    if "source" in df.columns:
        df["source"] = df["source"].apply(
            lambda s: s.get("name", "Unknown") if isinstance(s, dict) else str(s)
        )

    # ── 3. Rename columns to snake_case ───────────────────────
    df = df.rename(columns={"publishedAt": "published_at"})

    # ── 4. Drop rows missing title or description ─────────────
    df = df.dropna(subset=["title"])
    df["description"] = df["description"].fillna("")

    # ── 5. Strip HTML from text fields ────────────────────────
    df["title"]       = df["title"].apply(strip_html)
    df["description"] = df["description"].apply(strip_html)

    # ── 6. Remove duplicate articles (same title) ─────────────
    df = df.drop_duplicates(subset=["title"])

    # ── 7. Normalise published_at to UTC datetime ──────────────
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df = df.dropna(subset=["published_at"])

    # ── 8. Add a processing timestamp ─────────────────────────
    df["processed_at"] = datetime.utcnow().isoformat()

    dropped = original_count - len(df)
    log.info(f"Transform complete: {len(df)} clean rows ({dropped} dropped)")
    return df


if __name__ == "__main__":
    import json
    import glob

    # Find the most recent raw file and test transform on it
    files = sorted(glob.glob("data/raw/*.json"))
    if files:
        with open(files[-1]) as f:
            raw = json.load(f)
        df = transform(raw)
        print(df[["title", "source"]].head())
