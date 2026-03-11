"""
sentiment.py — Step 3: AI sentiment analysis using HuggingFace.
Uses a FREE pre-trained DistilBERT model — no training, no GPU needed.
"""

import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Load the AI model once at module start ─────────────────────
# This downloads the model (~250MB) on first run, then caches it.
# Every run after that is instant.
try:
    from transformers import pipeline as hf_pipeline
    sentiment_model = hf_pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512,
    )
    log.info("HuggingFace sentiment model loaded ✓")
except ImportError:
    sentiment_model = None
    log.warning("transformers not installed — sentiment will be skipped")


def analyse_sentiment(text: str) -> dict:
    """
    Runs AI sentiment analysis on a text string.

    Returns:
        {"label": "POSITIVE" | "NEGATIVE" | "NEUTRAL", "score": 0.0-1.0}

    The model was trained on movie/product reviews but generalises
    well to news headlines and article descriptions.
    """
    if not text or len(text.strip()) < 10:
        return {"label": "NEUTRAL", "score": 0.5}

    if sentiment_model is None:
        return {"label": "NEUTRAL", "score": 0.5}

    try:
        result = sentiment_model(text[:512])[0]
        log.debug(f"'{text[:60]}...' → {result['label']} ({result['score']:.3f})")
        return result
    except Exception as e:
        log.error(f"Sentiment analysis failed: {e}")
        return {"label": "NEUTRAL", "score": 0.0}


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds sentiment_label and sentiment_score columns to a DataFrame.
    Combines title + description for richer context.
    """
    if df.empty:
        return df

    log.info(f"Running sentiment analysis on {len(df)} articles...")

    results = []
    for _, row in df.iterrows():
        # Combine title and description for better accuracy
        combined_text = f"{row.get('title', '')} {row.get('description', '')}"
        result = analyse_sentiment(combined_text)
        results.append(result)

    df["sentiment_label"] = [r["label"] for r in results]
    df["sentiment_score"] = [round(r["score"], 4) for r in results]

    # Log a summary
    counts = df["sentiment_label"].value_counts().to_dict()
    log.info(f"Sentiment complete: {counts}")
    return df


if __name__ == "__main__":
    # Quick test
    samples = [
        "Apple reports record profits, stock surges 12%",
        "Major data breach exposes millions of user records",
        "Company releases quarterly earnings report",
    ]
    for text in samples:
        result = analyse_sentiment(text)
        print(f"{result['label']:10} ({result['score']:.2f})  →  {text}")
