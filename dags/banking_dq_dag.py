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
        logging.info("⏳ Running generate_data.py...")
        result = subprocess.run(
            ['python', '/opt/airflow/src/generate_data.py'],
            capture_output=True,
            text=True
        )
        if result.stdout:
            logging.info(f"[generate_data.py STDOUT]\n{result.stdout}")
        if result.stderr:
            logging.error(f"[generate_data.py STDERR]\n{result.stderr}")
        if result.returncode != 0:
            raise Exception("❌ generate_data.py failed.")
        logging.info("✅ generate_data.py completed successfully.")

    def run_quality_checks():
        logging.info("⏳ Running monitoring_audit.py...")
        result = subprocess.run(
            ['python', '/opt/airflow/src/monitoring_audit.py'],
            capture_output=True,
            text=True
        )
        if result.stdout:
            logging.info(f"[monitoring_audit.py STDOUT]\n{result.stdout}")
        if result.stderr:
            logging.error(f"[monitoring_audit.py STDERR]\n{result.stderr}")
        if result.returncode != 0:
            raise Exception("❌ monitoring_audit.py failed.")
        logging.info("✅ monitoring_audit.py completed successfully.")

    generate_data_task = PythonOperator(
        task_id='generate_data',
        python_callable=run_data_generation
    )

    run_audit_task = PythonOperator(
        task_id='run_quality_checks',
        python_callable=run_quality_checks
    )

    generate_data_task >> run_audit_task
