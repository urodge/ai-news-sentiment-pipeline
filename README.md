# 🤖 AI-Powered News Sentiment Pipeline

> An end-to-end automated data pipeline that fetches real news articles, runs AI sentiment analysis using HuggingFace, stores results in a cloud database, and exposes them via a REST API — orchestrated daily with Apache Airflow on Docker.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.7-017CEE?style=flat-square&logo=apacheairflow)
![Docker](https://img.shields.io/badge/Docker-Containerised-2496ED?style=flat-square&logo=docker)
![HuggingFace](https://img.shields.io/badge/HuggingFace-DistilBERT-FFD21E?style=flat-square&logo=huggingface)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?style=flat-square&logo=fastapi)
![GCP](https://img.shields.io/badge/GCP-BigQuery-4285F4?style=flat-square&logo=googlecloud)
![CI](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions)

---

## 📌 What This Project Does

Every day at 6am this pipeline automatically:
1. **Fetches** 100 tech news articles from NewsAPI
2. **Cleans** and deduplicates the raw data
3. **Analyses** each article's sentiment using a pre-trained AI model (DistilBERT)
4. **Loads** the enriched articles into PostgreSQL / GCP BigQuery
5. **Serves** results through a queryable REST API
6. **Alerts** via Slack if anything fails

This is a **Portfolio Project 2** — an intentional upgrade from a basic ETL pipeline (Project 1) to a cloud-deployed, AI-integrated, CI/CD-tested system.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APACHE AIRFLOW DAG                       │
│              Scheduled daily @ 06:00 UTC                    │
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│   INGEST    │───▶│  TRANSFORM   │───▶│   AI ANALYSIS   │
│  NewsAPI    │    │ Clean/Dedup  │    │ HuggingFace NLP │
│  100 arts.  │    │  Pandas      │    │  DistilBERT     │
└─────────────┘    └──────────────┘    └────────┬────────┘
                                                │
                                                ▼
                                    ┌─────────────────┐
                                    │      LOAD        │
                                    │  PostgreSQL /    │
                                    │  GCP BigQuery    │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   FastAPI        │
                                    │  REST Endpoint   │
                                    │ /articles        │
                                    │ /summary         │
                                    └─────────────────┘
```

---

## 🗂 Project Structure

```
ai-news-sentiment-pipeline/
│
├── pipeline/
│   ├── fetch_news.py          # Extract: pulls articles from NewsAPI
│   ├── transform.py           # Transform: clean, deduplicate, validate
│   ├── sentiment.py           # AI: HuggingFace sentiment scoring
│   ├── load.py                # Load: insert into PostgreSQL / BigQuery
│   └── alerts.py              # Slack webhook notifications
│
├── dags/
│   └── news_pipeline_dag.py   # Airflow DAG — orchestrates all tasks
│
├── api/
│   └── api.py                 # FastAPI REST endpoints
│
├── tests/
│   ├── test_transform.py      # Unit tests for data cleaning
│   └── test_sentiment.py      # Unit tests for AI layer
│
├── sql/
│   └── queries.sql            # Analytical SQL queries
│
├── .github/
│   └── workflows/
│       └── test.yml           # CI/CD — runs tests on every push
│
├── data/raw/                  # Raw JSON files from NewsAPI
├── docker-compose.yml         # Spins up Airflow + PostgreSQL + API
├── Dockerfile                 # Container definition for the API
├── requirements.txt           # Python dependencies
└── README.md
```

---

## 🛠 Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Ingestion | Python + requests | Fetch news from NewsAPI |
| Transform | Pandas | Clean, deduplicate, validate |
| AI Layer | HuggingFace Transformers | Sentiment analysis (DistilBERT) |
| Orchestration | Apache Airflow | DAG scheduling & monitoring |
| Containerisation | Docker + Docker Compose | Run everything locally & in cloud |
| Database | PostgreSQL / GCP BigQuery | Store enriched articles |
| API | FastAPI | REST endpoints for querying data |
| CI/CD | GitHub Actions | Auto-run tests on every push |
| Alerts | Slack Webhooks | Notify on pipeline success/failure |

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Free [NewsAPI key](https://newsapi.org) (takes 2 minutes)
- Free [GCP account](https://cloud.google.com) (optional — local SQLite works too)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-news-sentiment-pipeline.git
cd ai-news-sentiment-pipeline
```

### 2. Set your API key
```bash
cp .env.example .env
# Edit .env and add your NewsAPI key:
# NEWS_API_KEY=your_key_here
```

### 3. Start everything with Docker
```bash
docker-compose up -d
# Airflow UI  → http://localhost:8080  (user: airflow / pass: airflow)
# FastAPI     → http://localhost:8000/docs
```

### 4. Run without Docker (manual)
```bash
pip install -r requirements.txt
python pipeline/fetch_news.py
python pipeline/transform.py
python pipeline/sentiment.py
python pipeline/load.py
uvicorn api.api:app --reload  # starts API at localhost:8000
```

---

## 🤖 AI Sentiment Examples

```python
from pipeline.sentiment import analyse_sentiment

analyse_sentiment("Apple reports record profits, stock surges 12%")
# → {"label": "POSITIVE", "score": 0.98}

analyse_sentiment("Major data breach exposes millions of user records")
# → {"label": "NEGATIVE", "score": 0.97}

analyse_sentiment("Company releases quarterly earnings report")
# → {"label": "NEUTRAL", "score": 0.81}
```

---

## 📡 API Endpoints

```bash
# Get articles (with optional filters)
GET /articles?sentiment=NEGATIVE&days=7

# Get daily summary counts
GET /summary

# Health check
GET /health
```

**Example response:**
```json
[
  {
    "title": "Tech layoffs continue as market shifts",
    "source": "TechCrunch",
    "sentiment_label": "NEGATIVE",
    "sentiment_score": 0.94,
    "published_at": "2026-03-10T09:30:00Z"
  }
]
```

---

## 🗄 Sample SQL Queries

```sql
-- Sentiment breakdown for the past 7 days
SELECT sentiment_label, COUNT(*) AS count,
       ROUND(AVG(sentiment_score), 3) AS avg_confidence
FROM articles
WHERE published_at >= NOW() - INTERVAL '7 days'
GROUP BY sentiment_label
ORDER BY count DESC;

-- Most negative sources
SELECT source, COUNT(*) AS negative_count
FROM articles
WHERE sentiment_label = 'NEGATIVE'
GROUP BY source
ORDER BY negative_count DESC
LIMIT 10;
```

---

## ✅ Running Tests

```bash
pytest tests/ -v
# test_transform.py::test_drops_nulls         PASSED
# test_transform.py::test_deduplication        PASSED
# test_sentiment.py::test_positive_headline    PASSED
# test_sentiment.py::test_negative_headline    PASSED
# test_sentiment.py::test_empty_text_fallback  PASSED
```

Tests run automatically via **GitHub Actions** on every push to `main`.

---

## 📅 Development Timeline

- [x] Week 1 — NewsAPI ingestion + raw JSON storage
- [x] Week 2 — Transform layer + HuggingFace AI sentiment
- [x] Week 3 — PostgreSQL load + FastAPI REST endpoints
- [x] Week 4 — Airflow DAG on Docker + Slack alerts
- [x] Week 5 — pytest tests + GitHub Actions CI/CD
- [ ] Week 6 — GCP BigQuery deployment *(in progress)*

---

## 💡 Key Concepts Demonstrated

- **AI/ML Integration** — pre-trained NLP model via HuggingFace Transformers
- **Cloud-Native** — Docker containers, GCP BigQuery, free tier deployment
- **CI/CD Pipeline** — automated testing via GitHub Actions on every commit
- **REST API Design** — queryable FastAPI endpoints with filter parameters
- **Airflow Orchestration** — DAG with task dependencies, retries, and alerts
- **Data Engineering** — bronze → silver → gold data layer pattern

---

## 📖 What I Learned

- How to integrate pre-trained AI models into a data pipeline without training anything
- How Docker Compose simplifies running multi-service applications locally
- Why CI/CD matters — catching bugs before they reach production
- How REST APIs turn a backend pipeline into a usable product
- Cloud database patterns with GCP BigQuery

---

## 🔗 Related Projects

- 📦 [Project 1 — Weather ETL Pipeline]([https://github.com/YOUR_USERNAME/dataflow-automation-hub](https://github.com/urodge/ai-news-sentiment-pipeline)) — the foundational ETL project this builds on

---

## 📬 Contact

**Uddhav Rodge** — [LinkedIn](https://linkedin.com/in/uddhav-rodge-1501b7274) · [GitHub](https://github.com/urodge)

*Part of a portfolio series built while learning data engineering and automation engineering.*
