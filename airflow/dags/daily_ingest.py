"""
DAG: daily_ingest
Schedule: Twice daily — 6AM IST (00:30 UTC) and 6PM IST (12:30 UTC)
Purpose: Ingest live flight data from OpenSky Network API into Neon PostgreSQL
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    "owner": "shashank",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_ingest",
    default_args=default_args,
    description="Ingest live flight data from OpenSky Network API into Neon PostgreSQL",
    schedule_interval="30 0,12 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["ingestion", "flight-data-system"],
) as dag:

    check_db_connection = BashOperator(
        task_id="check_db_connection",
        bash_command="cd /opt/airflow && python ingestion/db_connection.py",
    )

    run_ingestion = BashOperator(
        task_id="run_ingestion",
        bash_command="cd /opt/airflow && python ingestion/opensky_api.py",
    )

    verify_data = BashOperator(
        task_id="verify_data",
        bash_command="cd /opt/airflow && python ingestion/verify_data.py",
    )

    check_db_connection >> run_ingestion >> verify_data