"""
alerts.py — Slack webhook notifications for pipeline events.
Set SLACK_WEBHOOK_URL in your .env file to enable alerts.
"""

import requests
import logging
import os

log = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def send_slack(message: str, emoji: str = "📊") -> bool:
    """
    Posts a message to a Slack channel via webhook.
    Returns True if successful, False otherwise.
    Free Slack workspace + incoming webhook = zero cost.
    """
    if not SLACK_WEBHOOK_URL:
        log.info("SLACK_WEBHOOK_URL not set — skipping alert")
        return False

    payload = {"text": f"{emoji}  {message}"}

    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        log.info("Slack alert sent ✓")
        return True
    except Exception as e:
        log.error(f"Slack alert failed: {e}")
        return False


def alert_success(articles_loaded: int, pos: int, neg: int, neu: int):
    send_slack(
        f"*News Pipeline — Run Complete ✅*\n"
        f"> Articles loaded: *{articles_loaded}*\n"
        f"> 🟢 Positive: {pos}  🔴 Negative: {neg}  ⚪ Neutral: {neu}",
        emoji="✅"
    )


def alert_failure(task_name: str, error: str):
    send_slack(
        f"*News Pipeline — FAILED ❌*\n"
        f"> Task: `{task_name}`\n"
        f"> Error: `{error}`",
        emoji="🚨"
    )
