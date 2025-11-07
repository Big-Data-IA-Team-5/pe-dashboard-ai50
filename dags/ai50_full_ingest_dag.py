"""Airflow DAG for full ingestion of Forbes AI 50 companies."""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


default_args = {
    'owner': 'pe-dashboard-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def scrape_all_task(**context):
    """Task 1: Scrape all company websites."""
    print("🔍 Starting web scraping...")
    
    # Import here to avoid issues
    import os
    os.chdir(str(project_root))
    
    from src.smart_scraper import scrape_all_smart
    results = scrape_all_smart()
    
    success_count = sum(1 for r in results if r['success'])
    print(f"✅ Scraped {success_count}/50 companies")
    
    return {'success_count': success_count, 'total': 50}


def scrape_selenium_jobs_task(**context):
    """Task 2: Scrape careers pages with Selenium."""
    print("💼 Scraping careers pages...")
    
    import os
    os.chdir(str(project_root))
    
    # Run selenium scraper
    import subprocess
    result = subprocess.run(
        ['python', 'src/scrape_jobs_selenium.py'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    return {'status': 'complete'}


def extract_structured_task(**context):
    """Task 3: Extract structured data with Instructor."""
    print("🔍 Extracting structured data...")
    
    import os
    os.chdir(str(project_root))
    
    from src.extractor_enhanced import extract_all_complete
    results = extract_all_complete()
    
    success_count = sum(1 for r in results if r['success'])
    print(f"✅ Extracted {success_count} companies")
    
    return {'extracted': success_count}


def extract_jobs_task(**context):
    """Task 4: Extract job openings."""
    print("💼 Extracting job openings...")
    
    import os
    os.chdir(str(project_root))
    
    from src.extract_selenium_jobs import extract_all_selenium_jobs
    results = extract_all_selenium_jobs()
    
    total_jobs = sum(r['total'] for r in results)
    print(f"✅ Extracted {total_jobs} total jobs")
    
    return {'total_jobs': total_jobs}


def merge_jobs_task(**context):
    """Task 5: Merge jobs into payloads."""
    print("🔗 Merging jobs into payloads...")
    
    import os
    os.chdir(str(project_root))
    
    # Run merge script
    import subprocess
    result = subprocess.run(
        ['python', 'merge_final_jobs.py'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    return {'status': 'merged'}


def index_vector_db_task(**context):
    """Task 6: Index in ChromaDB."""
    print("📚 Building vector database...")
    
    import os
    os.chdir(str(project_root))
    
    from src.vector_db import index_all_companies
    results = index_all_companies()
    
    total_chunks = sum(r['chunks'] for r in results)
    print(f"✅ Indexed {total_chunks} chunks")
    
    return {'total_chunks': total_chunks}


with DAG(
    'ai50_full_ingest',
    default_args=default_args,
    description='Complete ingestion pipeline for Forbes AI 50',
    schedule_interval='@monthly',  # Run once per month
    catchup=False,
    tags=['ai50', 'full-pipeline', 'production'],
) as dag:
    
    # Task 1: Scrape websites
    scrape = PythonOperator(
        task_id='scrape_websites',
        python_callable=scrape_all_task,
    )
    
    # Task 2: Scrape careers with Selenium
    scrape_careers = PythonOperator(
        task_id='scrape_careers_selenium',
        python_callable=scrape_selenium_jobs_task,
    )
    
    # Task 3: Extract structured data
    extract = PythonOperator(
        task_id='extract_structured_data',
        python_callable=extract_structured_task,
    )
    
    # Task 4: Extract jobs
    extract_jobs = PythonOperator(
        task_id='extract_job_openings',
        python_callable=extract_jobs_task,
    )
    
    # Task 5: Merge jobs
    merge_jobs = PythonOperator(
        task_id='merge_jobs_into_payloads',
        python_callable=merge_jobs_task,
    )
    
    # Task 6: Build vector DB
    index_vector = PythonOperator(
        task_id='index_vector_database',
        python_callable=index_vector_db_task,
    )
    
    # Pipeline flow
    scrape >> scrape_careers >> extract >> extract_jobs >> merge_jobs >> index_vector