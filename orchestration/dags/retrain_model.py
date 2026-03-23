"""
DAG: retrain_model
Schedule: Twice daily — triggered after dbt_transform completes
Purpose: Engineer features and retrain XGBoost delay prediction model
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
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

def check_data_sufficiency(**context):
    import os
    from sqlalchemy import create_engine, text
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM ml.features"))
        count = result.scalar()
    print(f"ml.features row count: {count}")
    if count >= 100:
        return "run_feature_engineering"
    else:
        return "skip_retraining"

with DAG(
    dag_id="retrain_model",
    default_args=default_args,
    description="Engineer features and retrain XGBoost delay prediction model",
    schedule_interval="0 1,13 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["ml", "xgboost", "mlflow", "flight-data-system"],
) as dag:

    wait_for_dbt = ExternalTaskSensor(
        task_id="wait_for_dbt",
        external_dag_id="dbt_transform",
        external_task_id="dbt_test",
        timeout=600,
        poke_interval=30,
        mode="poke",
    )

    check_data = BranchPythonOperator(
        task_id="check_data_sufficiency",
        python_callable=check_data_sufficiency,
        provide_context=True,
    )

    run_feature_engineering = BashOperator(
        task_id="run_feature_engineering",
        bash_command="cd /opt/airflow && python transform/feature_engineering.py",
    )

    skip_retraining = BashOperator(
        task_id="skip_retraining",
        bash_command='echo "Skipping retraining — insufficient data in ml.features"',
    )

    retrain_model = BashOperator(
        task_id="retrain_model",
        bash_command="cd /opt/airflow && python ml/train.py",
    )

    verify_model = BashOperator(
        task_id="verify_model",
        bash_command=(
            "test -f /opt/airflow/ml/models/flight_delay_model.pkl && "
            "echo 'Model file verified' || "
            "echo 'Model file missing' && exit 1"
        ),
    )

    wait_for_dbt >> check_data
    check_data >> run_feature_engineering >> retrain_model >> verify_model
    check_data >> skip_retraining