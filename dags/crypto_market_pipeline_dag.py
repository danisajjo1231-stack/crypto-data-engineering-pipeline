from datetime import timedelta

import pendulum

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ROOT = (
    "/mnt/c/Users/HP/OneDrive/Desktop/Danish Data/crypto_data_pipeline"
)

PYTHON_EXE = (
    "/mnt/c/Users/HP/OneDrive/Desktop/Danish Data/"
    "crypto_data_pipeline/.venv/Scripts/python.exe"
)

PIPELINE_SCRIPT = (
    "C:/Users/HP/OneDrive/Desktop/Danish Data/"
    "crypto_data_pipeline/crypto_pipeline.py"
)

PAKISTAN_TZ = pendulum.timezone("Asia/Karachi")

default_args = {
    "owner": "danish",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email": ["afridid476@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}

with DAG(
    dag_id="crypto_market_pipeline",
    description="Automated cryptocurrency data engineering pipeline",
    default_args=default_args,
    start_date=pendulum.datetime(2026, 10, 17, tz=PAKISTAN_TZ),
    schedule="0 8 * * *",
    catchup=False,
    tags=["crypto", "data-engineering", "sql-server"],
) as dag:

    run_crypto_pipeline = BashOperator(
        task_id="extract_validate_transform_load",
        bash_command=f'"{PYTHON_EXE}" "{PIPELINE_SCRIPT}"',
        cwd=PROJECT_ROOT,
    )
