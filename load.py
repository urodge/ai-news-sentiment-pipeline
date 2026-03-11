"""
load.py — Step 4: Load enriched articles into PostgreSQL or SQLite.
SQLite works locally with zero setup. Swap DB_URL for PostgreSQL in production.
"""

import sqlite3
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Use SQLite locally, PostgreSQL in production ───────────────
DB_PATH = os.getenv("DB_PATH", "news.db")


def create_table(conn):
    """Creates the articles table if it doesn't already exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            title            TEXT    NOT NULL,
            description      TEXT,
            source           TEXT,
            url              TEXT    UNIQUE,
            published_at     DATETIME,
            processed_at     DATETIME,
            sentiment_label  TEXT,
            sentiment_score  REAL,
            loaded_at        DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    log.info("Table 'articles' ready ✓")


def load(df: pd.DataFrame) -> int:
    """
    Inserts enriched articles DataFrame into the database.
    Skips rows with duplicate URLs (UNIQUE constraint).
    Returns number of rows inserted.
    """
    if df.empty:
        log.warning("Nothing to load — DataFrame is empty")
        return 0

    conn = sqlite3.connect(DB_PATH)

    try:
        create_table(conn)

        # Only keep columns that exist in the table schema
        db_cols = ["title", "description", "source", "url",
                   "published_at", "processed_at", "sentiment_label", "sentiment_score"]
        df_to_load = df[[c for c in db_cols if c in df.columns]]

        # Insert rows, ignoring duplicates (same URL already exists)
        inserted = 0
        for _, row in df_to_load.iterrows():
            try:
                conn.execute(
                    f"INSERT OR IGNORE INTO articles ({', '.join(df_to_load.columns)}) "
                    f"VALUES ({', '.join(['?'] * len(df_to_load.columns))})",
                    tuple(row)
                )
                if conn.total_changes > inserted:
                    inserted = conn.total_changes
            except Exception as e:
                log.warning(f"Skipped row: {e}")

        conn.commit()
        log.info(f"Load complete → {inserted} new rows inserted into '{DB_PATH}'")
        return inserted

    except Exception as e:
        log.error(f"Load failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Quick test with dummy data
    test_df = pd.DataFrame([{
        "title": "Test Article",
        "description": "This is a test",
        "source": "TestSource",
        "url": "https://example.com/test",
        "published_at": "2026-03-11T06:00:00Z",
        "processed_at": "2026-03-11T06:01:00",
        "sentiment_label": "NEUTRAL",
        "sentiment_score": 0.75,
    }])
    load(test_df)
