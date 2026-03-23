"""
DAG: dbt_transform
Schedule: Twice daily — triggered after daily_ingest completes
Purpose: Run dbt models (staging → warehouse → mart) and data quality tests
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.dates import days_ago

default_args = {
    "owner": "shashank",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dbt_transform",
    default_args=default_args,
    description="Run dbt transformations and data quality tests after ingestion",
    schedule_interval="45 0,12 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["transformation", "dbt", "flight-data-system"],
) as dag:

    wait_for_ingestion = ExternalTaskSensor(
        task_id="wait_for_ingestion",
        external_dag_id="daily_ingest",
        external_task_id="verify_data",
        timeout=600,
        poke_interval=30,
        mode="poke",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/airflow/transform/flight_transform && "
            "dbt run --profiles-dir /opt/airflow/transform/flight_transform"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "cd /opt/airflow/transform/flight_transform && "
            "dbt test --profiles-dir /opt/airflow/transform/flight_transform"
        ),
    )

    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            "cd /opt/airflow/transform/flight_transform && "
            "dbt docs generate --profiles-dir /opt/airflow/transform/flight_transform"
        ),
    )

    wait_for_ingestion >> dbt_run >> dbt_test >> dbt_docs_generate