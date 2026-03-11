-- ─────────────────────────────────────────────────────────────
-- queries.sql — Analytical SQL for the News Sentiment Pipeline
-- Run: sqlite3 news.db < sql/queries.sql
-- ─────────────────────────────────────────────────────────────


-- 1. OVERALL SENTIMENT BREAKDOWN
SELECT sentiment_label,
       COUNT(*)                       AS article_count,
       ROUND(AVG(sentiment_score),3)  AS avg_confidence,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentage
FROM   articles
GROUP  BY sentiment_label
ORDER  BY article_count DESC;


-- 2. DAILY TREND — how has sentiment changed over time?
SELECT DATE(published_at)  AS date,
       sentiment_label,
       COUNT(*)             AS count
FROM   articles
GROUP  BY DATE(published_at), sentiment_label
ORDER  BY date DESC;


-- 3. MOST NEGATIVE SOURCES
SELECT source,
       COUNT(*) AS negative_articles
FROM   articles
WHERE  sentiment_label = 'NEGATIVE'
GROUP  BY source
ORDER  BY negative_articles DESC
LIMIT  10;


-- 4. HIGHEST CONFIDENCE PREDICTIONS (AI most certain)
SELECT title, sentiment_label, sentiment_score, source
FROM   articles
WHERE  sentiment_score > 0.95
ORDER  BY sentiment_score DESC
LIMIT  20;


-- 5. PIPELINE HEALTH — rows loaded per day
SELECT DATE(loaded_at)  AS run_date,
       COUNT(*)          AS rows_loaded
FROM   articles
GROUP  BY DATE(loaded_at)
ORDER  BY run_date DESC;
