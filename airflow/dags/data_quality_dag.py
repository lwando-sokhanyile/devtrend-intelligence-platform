"""
Data Quality DAG
================
Triggered automatically after dbt_transform_dag completes.
Runs dbt tests on all models and alerts on failure.

Author: Lwando Sokhanyile
Project: DevTrend Intelligence Platform
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# ── Default arguments ─────────────────────────────────────────────────────────
default_args = {
    "owner":            "lwando",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
}

# ── DAG Definition ────────────────────────────────────────────────────────────
with DAG(
    dag_id="data_quality_dag",
    description="Runs dbt tests after transformation and alerts on failure",
    default_args=default_args,
    start_date=datetime(2026, 7, 28),
    schedule_interval=None,   # only triggered by dbt_transform_dag
    catchup=False,
    tags=["dbt", "quality", "testing"],
) as dag:

    # ── Task 1: Test staging models ───────────────────────────────────────────
    test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command="cd /dbt && dbt test --select staging",
    )

    # ── Task 2: Test intermediate models ──────────────────────────────────────
    test_intermediate = BashOperator(
        task_id="dbt_test_intermediate",
        bash_command="cd /dbt && dbt test --select intermediate",
    )

    # ── Task 3: Test mart models ──────────────────────────────────────────────
    test_marts = BashOperator(
        task_id="dbt_test_marts",
        bash_command="cd /dbt && dbt test --select marts",
    )

    # ── Task Dependencies ─────────────────────────────────────────────────────
    # test in the same order as they were built
    test_staging >> test_intermediate >> test_marts