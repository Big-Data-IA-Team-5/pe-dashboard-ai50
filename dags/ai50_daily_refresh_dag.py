"""Airflow DAG for daily refresh of company data."""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

default_args = {
    'owner': 'pe-dashboard-team',
    'start_date': datetime(2025, 11, 1),
    'retries': 1,
}


def refresh_careers_task(**context):
    """Re-scrape careers pages only."""
    print("🔄 Refreshing careers pages...")
    
    import os
    os.chdir(str(project_root))
    
    import subprocess
    result = subprocess.run(
        ['python', 'src/scrape_jobs_selenium.py'],
        capture_output=True,
        text=True
    )
    
    print("✅ Careers pages refreshed")
    return {'status': 'refreshed'}


def refresh_jobs_task(**context):
    """Re-extract and merge jobs."""
    print("💼 Refreshing job openings...")
    
    import os
    os.chdir(str(project_root))
    
    # Extract jobs
    from src.extract_selenium_jobs import extract_all_selenium_jobs
    extract_all_selenium_jobs()
    
    # Merge jobs
    import subprocess
    subprocess.run(['python', 'merge_final_jobs.py'])
    
    print("✅ Jobs refreshed")
    return {'status': 'refreshed'}


def update_vector_db_task(**context):
    """Re-index vector database."""
    print("📚 Updating vector database...")
    
    import os
    os.chdir(str(project_root))
    
    from src.vector_db import index_all_companies
    index_all_companies()
    
    print("✅ Vector DB updated")
    return {'status': 'updated'}


with DAG(
    'ai50_daily_refresh',
    default_args=default_args,
    description='Daily refresh of careers and job data',
    schedule_interval='0 3 * * *',  # 3 AM daily
    catchup=False,
    tags=['ai50', 'daily', 'refresh'],
) as dag:
    
    refresh_careers = PythonOperator(
        task_id='refresh_careers_pages',
        python_callable=refresh_careers_task,
    )
    
    refresh_jobs = PythonOperator(
        task_id='refresh_job_openings',
        python_callable=refresh_jobs_task,
    )
    
    update_vectordb = PythonOperator(
        task_id='update_vector_database',
        python_callable=update_vector_db_task,
    )
    
    # Pipeline: Scrape careers → Extract jobs → Update vector DB
    refresh_careers >> refresh_jobs >> update_vectordb
