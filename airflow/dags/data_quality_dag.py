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


default_args = {
    "owner":            "lwando",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
}

with DAG(
    dag_id="data_quality_dag",
    description="Runs dbt tests after transformation and alerts on failure",
    default_args=default_args,
    start_date=datetime(2026, 7, 28),
    schedule_interval=None,   # only triggered by dbt_transform_dag
    catchup=False,
    tags=["dbt", "quality", "testing"],
) as dag:

    test_staging = BashOperator(
        task_id="dbt_test_staging",
        bash_command="cd /opt/airflow/dbt && dbt test --select staging",
    )


    test_intermediate = BashOperator(
        task_id="dbt_test_intermediate",
        bash_command="cd /opt/airflow/dbt && dbt test --select intermediate",
    )

    test_marts = BashOperator(
        task_id="dbt_test_marts",
        bash_command="cd /opt/airflow/dbt && dbt test --select marts",
    )

   
    test_staging >> test_intermediate >> test_marts