"""
news_pipeline_dag.py — Apache Airflow DAG
Orchestrates the full news sentiment pipeline daily at 06:00 UTC.
Place this file in your Airflow dags/ folder.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pipeline'))

from fetch_news import fetch_news
from transform  import transform
from sentiment  import enrich_dataframe
from load       import load
from alerts     import alert_success, alert_failure

# ── Default arguments for all tasks ───────────────────────────
default_args = {
    "owner": "your_name",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["you@example.com"],
}

# ── Callable wrappers (Airflow passes context via kwargs) ──────
def run_fetch(**kwargs):
    articles = fetch_news(query="artificial intelligence")
    kwargs["ti"].xcom_push(key="articles", value=articles)


def run_transform(**kwargs):
    articles = kwargs["ti"].xcom_pull(key="articles", task_ids="fetch_news")
    df = transform(articles)
    kwargs["ti"].xcom_push(key="clean_df_json", value=df.to_json())


def run_sentiment(**kwargs):
    import pandas as pd, io
    df_json = kwargs["ti"].xcom_pull(key="clean_df_json", task_ids="transform")
    df = pd.read_json(io.StringIO(df_json))
    df = enrich_dataframe(df)
    kwargs["ti"].xcom_push(key="enriched_df_json", value=df.to_json())


def run_load(**kwargs):
    import pandas as pd, io
    df_json = kwargs["ti"].xcom_pull(key="enriched_df_json", task_ids="sentiment")
    df = pd.read_json(io.StringIO(df_json))
    inserted = load(df)
    counts = df["sentiment_label"].value_counts().to_dict()
    alert_success(
        articles_loaded=inserted,
        pos=counts.get("POSITIVE", 0),
        neg=counts.get("NEGATIVE", 0),
        neu=counts.get("NEUTRAL", 0),
    )


# ── DAG definition ─────────────────────────────────────────────
with DAG(
    dag_id="news_sentiment_pipeline",
    default_args=default_args,
    description="Daily AI-powered news sentiment ETL pipeline",
    schedule_interval="0 6 * * *",   # Every day at 06:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["news", "ai", "sentiment", "etl"],
) as dag:

    t1 = PythonOperator(task_id="fetch_news",   python_callable=run_fetch,     provide_context=True)
    t2 = PythonOperator(task_id="transform",    python_callable=run_transform, provide_context=True)
    t3 = PythonOperator(task_id="sentiment",    python_callable=run_sentiment, provide_context=True)
    t4 = PythonOperator(task_id="load",         python_callable=run_load,      provide_context=True)

    # ── Task order: fetch → clean → AI → store ─────────────────
    t1 >> t2 >> t3 >> t4
