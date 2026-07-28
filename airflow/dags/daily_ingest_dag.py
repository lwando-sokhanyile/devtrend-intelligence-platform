"""
Daily Ingest DAG
================
Runs all three collectors every day at 06:00 UTC.

Order:
1. repos_collector.py
2. languages_collector.py
3. developers_collector.py

If any task fails, Airflow retries it 3 times
before marking it as failed and sending an alert.

Author: Lwando Sokhanyile
Project: DevTrend Intelligence Platform
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# ── Default arguments applied to every task ───────────────────────────────────
default_args = {
    "owner":            "lwando",
    "depends_on_past":  False,
    "email_on_failure": False,   # set to True and add email when ready
    "email_on_retry":   False,
    "retries":          3,
    "retry_delay":      timedelta(minutes=5),
}

# ── DAG Definition ────────────────────────────────────────────────────────────
with DAG(
    dag_id="daily_ingest_dag",
    description="Runs all GitHub trending collectors daily",
    default_args=default_args,
    start_date=datetime(2026, 7, 28),
    schedule_interval="0 6 * * *",   # every day at 06:00 UTC
    catchup=False,                    # don't backfill missed runs
    tags=["ingestion", "github", "daily"],
) as dag:

    # ── Task 1: Repos Collector ───────────────────────────────────────────────
    run_repos_collector = BashOperator(
        task_id="run_repos_collector",
        bash_command="cd /opt/airflow && python src/collectors/repos_collector.py",
    )

    # ── Task 2: Languages Collector ───────────────────────────────────────────
    run_languages_collector = BashOperator(
        task_id="run_languages_collector",
        bash_command="cd /opt/airflow && python src/collectors/languages_collector.py",
    )

    # ── Task 3: Developers Collector ──────────────────────────────────────────
    run_developers_collector = BashOperator(
        task_id="run_developers_collector",
        bash_command="cd /opt/airflow && python src/collectors/developers_collector.py",
    )

    # ── Task 4: Trigger dbt transform DAG ─────────────────────────────────────
    trigger_dbt = TriggerDagRunOperator(
        task_id="trigger_dbt_transform",
        trigger_dag_id="dbt_transform_dag",
        wait_for_completion=False,  # don't wait — let it run independently
    )

    # ── Task Dependencies ─────────────────────────────────────────────────────
    # repos → languages → developers → trigger dbt
    # Each task only runs after the previous one succeeds
    run_repos_collector >> run_languages_collector >> run_developers_collector >> trigger_dbt