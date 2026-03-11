"""
api.py — FastAPI REST API to query pipeline results.
Run with: uvicorn api.api:app --reload
Docs at:  http://localhost:8000/docs
"""

from fastapi import FastAPI, Query
from typing import Optional
import sqlite3
import pandas as pd

app = FastAPI(
    title="News Sentiment API",
    description="Query AI-enriched news articles from the automated pipeline.",
    version="1.0.0",
)

DB_PATH = "news.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


@app.get("/health")
def health():
    """Health check — confirms the API is running."""
    return {"status": "ok", "service": "News Sentiment API"}


@app.get("/articles")
def get_articles(
    sentiment: Optional[str] = Query(None, description="POSITIVE, NEGATIVE, or NEUTRAL"),
    days: int = Query(7, description="How many days back to look"),
    limit: int = Query(50, description="Max number of results"),
):
    """
    Returns news articles with their AI sentiment scores.

    Examples:
    - /articles?sentiment=NEGATIVE&days=3
    - /articles?sentiment=POSITIVE&limit=10
    """
    conn = get_conn()
    query = f"""
        SELECT title, source, sentiment_label,
               ROUND(sentiment_score, 3) AS sentiment_score,
               published_at
        FROM   articles
        WHERE  published_at >= DATE('now', '-{days} days')
    """
    if sentiment:
        query += f" AND sentiment_label = '{sentiment.upper()}'"

    query += f" ORDER BY published_at DESC LIMIT {limit}"

    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/summary")
def get_summary():
    """
    Returns daily counts of POSITIVE / NEGATIVE / NEUTRAL articles.
    Useful for tracking sentiment trends over time.
    """
    conn = get_conn()
    df = pd.read_sql("""
        SELECT DATE(published_at)   AS date,
               sentiment_label,
               COUNT(*)             AS count,
               ROUND(AVG(sentiment_score), 3) AS avg_score
        FROM   articles
        GROUP  BY DATE(published_at), sentiment_label
        ORDER  BY date DESC
    """, conn)
    conn.close()
    return df.to_dict(orient="records")


@app.get("/sources")
def get_top_sources():
    """Returns the top news sources by article count."""
    conn = get_conn()
    df = pd.read_sql("""
        SELECT source,
               COUNT(*)  AS total_articles,
               SUM(CASE WHEN sentiment_label='POSITIVE' THEN 1 ELSE 0 END) AS positive,
               SUM(CASE WHEN sentiment_label='NEGATIVE' THEN 1 ELSE 0 END) AS negative
        FROM   articles
        GROUP  BY source
        ORDER  BY total_articles DESC
        LIMIT  20
    """, conn)
    conn.close()
    return df.to_dict(orient="records")
