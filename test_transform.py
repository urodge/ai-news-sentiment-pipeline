"""
test_transform.py — Unit tests for the transform pipeline step.
Run with: pytest tests/ -v
"""

import pytest
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pipeline'))

from transform import transform, strip_html


# ── Test: HTML stripping ───────────────────────────────────────
def test_strip_html_removes_tags():
    assert strip_html("<b>Hello</b> World") == "Hello World"

def test_strip_html_handles_empty():
    assert strip_html("") == ""
    assert strip_html(None) == ""


# ── Test: transform drops rows with no title ──────────────────
def test_drops_rows_missing_title():
    articles = [
        {"title": "Valid Article", "description": "desc", "source": {"name": "BBC"},
         "url": "http://a.com", "publishedAt": "2026-03-11T06:00:00Z"},
        {"title": None, "description": "no title", "source": {"name": "CNN"},
         "url": "http://b.com", "publishedAt": "2026-03-11T06:00:00Z"},
    ]
    df = transform(articles)
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Valid Article"


# ── Test: deduplication removes same title ────────────────────
def test_deduplication_removes_duplicates():
    articles = [
        {"title": "Same Headline", "description": "a", "source": {"name": "S1"},
         "url": "http://1.com", "publishedAt": "2026-03-11T06:00:00Z"},
        {"title": "Same Headline", "description": "b", "source": {"name": "S2"},
         "url": "http://2.com", "publishedAt": "2026-03-11T06:00:00Z"},
    ]
    df = transform(articles)
    assert len(df) == 1


# ── Test: empty input returns empty DataFrame ─────────────────
def test_empty_input_returns_empty_df():
    df = transform([])
    assert df.empty


# ── Test: source column is flattened from dict ────────────────
def test_source_column_flattened():
    articles = [
        {"title": "Article", "description": "d", "source": {"name": "Reuters"},
         "url": "http://x.com", "publishedAt": "2026-03-11T06:00:00Z"},
    ]
    df = transform(articles)
    assert df.iloc[0]["source"] == "Reuters"
