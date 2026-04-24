from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import sys
import pandas as pd

sys.path.append("/opt/airflow/scripts")

from extract import extract_data
from transform import transform_data
from load import load_to_s3
from explore_s3 import explore_s3

default_args = {
    "owner": "data_engineer",
    "retries": 2,
    "retry_delay": timedelta(minutes=2)
}

def extract_task(**context):
    df = extract_data("/opt/airflow/data/sales1.csv")
    context["ti"].xcom_push(key="df", value=df.to_json())

def transform_task(**context):
    df = pd.read_json(context["ti"].xcom_pull(key="df"))
    df = transform_data(df)
    context["ti"].xcom_push(key="df", value=df.to_json())

def load_task(**context):
    df = pd.read_json(context["ti"].xcom_pull(key="df"))
    load_to_s3(
        df,
        bucket="sales1-bucket",
        key="output/sales1.csv",
        endpoint="http://localstack:4566"
    )

def explore_s3_task(**context):
    explore_s3(
        bucket="sales1-bucket",
        key="output/sales.csv",
        endpoint="http://localstack:4566"
    )

with DAG(
    dag_id="etl_oracle_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args
) as dag:

    extract_op = PythonOperator(
        task_id="extract",
        python_callable=extract_task
    )

    transform_op = PythonOperator(
        task_id="transform",
        python_callable=transform_task
    )

    load_op = PythonOperator(
        task_id="load",
        python_callable=load_task
    )

    explore_s3_op = PythonOperator( 
        task_id="explore_s3",
        python_callable=explore_s3_task
    )

    extract_op >> transform_op >> load_op >> explore_s3_op