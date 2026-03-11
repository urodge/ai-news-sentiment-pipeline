"""
test_sentiment.py — Unit tests for the AI sentiment layer.
Uses simple rule checks so tests run fast without loading the full model.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pipeline'))

from sentiment import analyse_sentiment


# ── Test: empty / short text returns NEUTRAL ─────────────────
def test_empty_text_returns_neutral():
    result = analyse_sentiment("")
    assert result["label"] == "NEUTRAL"

def test_short_text_returns_neutral():
    result = analyse_sentiment("hi")
    assert result["label"] == "NEUTRAL"


# ── Test: result always has required keys ─────────────────────
def test_result_has_label_and_score():
    result = analyse_sentiment("Some news headline about technology")
    assert "label" in result
    assert "score" in result


# ── Test: score is between 0 and 1 ───────────────────────────
def test_score_is_valid_range():
    result = analyse_sentiment("Breaking news about a major company merger")
    assert 0.0 <= result["score"] <= 1.0


# ── Test: label is one of the valid values ────────────────────
def test_label_is_valid():
    result = analyse_sentiment("Technology stocks rise sharply today")
    assert result["label"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
