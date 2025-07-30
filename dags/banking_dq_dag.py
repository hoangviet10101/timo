from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import subprocess
import logging

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='banking_data_quality_pipeline',
    default_args=default_args,
    description='Run daily data generation and quality checks for banking DB',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['banking', 'data_quality', 'monitoring'],
) as dag:

    def run_data_generation():
        try:
            result = subprocess.run(['python', '/opt/airflow/src/generate_data.py'], check=True)
            logging.info("✅ Data generation completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error("❌ Data generation failed!")
            raise e

    def run_quality_checks():
        try:
            result = subprocess.run(['python', '/opt/airflow/src/monitoring_audit.py'], check=True)
            logging.info("✅ Data quality checks completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error("❌ Data quality checks failed!")
            raise e

    generate_data_task = PythonOperator(
        task_id='generate_data',
        python_callable=run_data_generation
    )

    run_audit_task = PythonOperator(
        task_id='run_quality_checks',
        python_callable=run_quality_checks
    )

    generate_data_task >> run_audit_task
