"""
dbt Transform DAG
=================
Triggered automatically after daily_ingest_dag completes.
Runs the full dbt pipeline in order:
1. dbt run --select staging
2. dbt run --select intermediate
3. dbt run --select marts
4. Triggers data_quality_dag

Author: Lwando Sokhanyile
Project: DevTrend Intelligence Platform
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    "owner":            "lwando",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          2,
    "retry_delay":      timedelta(minutes=5),
}

with DAG(
    dag_id="dbt_transform_dag",
    description="Runs dbt staging, intermediate and mart models after ingestion",
    default_args=default_args,
    start_date=datetime(2026, 7, 28),
    schedule_interval=None,   
    catchup=False,
    tags=["dbt", "transformation"],
) as dag:

    dbt_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command="cd /opt/airflow/dbt && dbt run --select staging",
    )

    dbt_intermediate = BashOperator(
        task_id="dbt_run_intermediate",
        bash_command="cd /opt/airflow/dbt && dbt run --select intermediate",
    )

    dbt_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command="cd /opt/airflow/dbt && dbt run --select marts",
    )

    trigger_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality_dag",
        wait_for_completion=False,
    )

    dbt_staging >> dbt_intermediate >> dbt_marts >> trigger_quality