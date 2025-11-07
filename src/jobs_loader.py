"""Load job data from GCS for dashboard enrichment."""
import os
import json
from pathlib import Path
from google.cloud import storage
from typing import Dict, List


class JobsLoader:
    """Load jobs data from GCS or local."""
    
    def __init__(self, use_gcs: bool = None):
        """Initialize jobs loader."""
        self.bucket_name = "us-central1-pe-airflow-env-2825d831-bucket"
        self.gcs_path = "data/jobs/"
        self.local_path = Path("data/jobs")
        
        # Create local jobs directory if it doesn't exist
        self.local_path.mkdir(parents=True, exist_ok=True)
        
        # Check local jobs availability
        local_jobs_count = len(list(self.local_path.glob("*.json")))  # Changed pattern
        
        if use_gcs is None:
            # Prefer LOCAL if we have jobs files
            if local_jobs_count > 0:
                use_gcs = False
                print(f"📂 Found {local_jobs_count} local jobs files, using local data...")
            else:
                use_gcs = True
                print("📥 No local jobs, will try GCS...")
        
        self.use_gcs = use_gcs
        self.jobs_cache = {}
        self.jobs_available = False
    
    def get_jobs_for_company(self, company_id: str) -> List[Dict]:
        """
        Get job listings for a company.
        
        Args:
            company_id: Company identifier
            
        Returns:
            List of job dicts with title, location, description, etc.
        """
        # Check cache
        if company_id in self.jobs_cache:
            return self.jobs_cache[company_id]
        
        jobs = []
        
        try:
            if self.use_gcs:
                jobs = self._load_from_gcs(company_id)
            else:
                jobs = self._load_from_local(company_id)
            
            # Cache it
            self.jobs_cache[company_id] = jobs
            
        except Exception as e:
            print(f"  ⚠️  Could not load jobs for {company_id}: {e}")
            jobs = []
        
        return jobs
    
    def _load_from_gcs(self, company_id: str) -> List[Dict]:
        """Load jobs from GCS."""
        try:
            key_file = os.getenv("GCP_SERVICE_ACCOUNT_KEY", "./gcp-service-account-key.json")
            
            if Path(key_file).exists():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file
            
            client = storage.Client(project="pe-dashboard-ai50")
            bucket = client.bucket(self.bucket_name)
            
            # Try to find job file
            blob_path = f"{self.gcs_path}{company_id}_jobs.json"
            blob = bucket.blob(blob_path)
            
            if blob.exists():
                content = blob.download_as_text()
                jobs = json.loads(content)
                print(f"    ✓ Loaded {len(jobs)} jobs from GCS for {company_id}")
                return jobs
            else:
                print(f"    ⚠️  No jobs file found in GCS: {blob_path}")
                return []
        except Exception as e:
            print(f"    ⚠️  GCS error for {company_id}: {e}")
            # Fallback to local if GCS fails
            return self._load_from_local(company_id)
    
    def _load_from_local(self, company_id: str) -> List[Dict]:
        """Load jobs from local file."""
        # Try both patterns: company_id.json and company_id_jobs.json
        job_file = self.local_path / f"{company_id}.json"
        if not job_file.exists():
            job_file = self.local_path / f"{company_id}_jobs.json"
        
        if job_file.exists():
            data = json.loads(job_file.read_text())
            
            # Handle different formats
            if isinstance(data, dict) and 'jobs' in data:
                # Format: {"jobs": [...], "total_openings": X, ...}
                jobs = data['jobs']
            elif isinstance(data, list):
                # Format: [{"title": ..., ...}, ...]
                jobs = data
            else:
                jobs = []
            
            if jobs:
                print(f"    ✓ Loaded {len(jobs)} jobs from local file: {job_file.name}")
            return jobs
        
        return []
    
    def get_job_summary(self, company_id: str) -> Dict:
        """Get summary of jobs for a company."""
        jobs = self.get_jobs_for_company(company_id)
        
        if not jobs:
            return {
                "total_jobs": 0,
                "engineering_jobs": 0,
                "sales_jobs": 0,
                "other_jobs": 0,
                "available": False
            }
        
        # Categorize jobs
        engineering = sum(1 for j in jobs if any(kw in j.get('title', '').lower() 
                         for kw in ['engineer', 'developer', 'technical', 'software']))
        sales = sum(1 for j in jobs if any(kw in j.get('title', '').lower() 
                    for kw in ['sales', 'account', 'business development']))
        
        return {
            "total_jobs": len(jobs),
            "engineering_jobs": engineering,
            "sales_jobs": sales,
            "other_jobs": len(jobs) - engineering - sales,
            "available": True,
            "sample_titles": [j.get('title', 'Unknown') for j in jobs[:3]]
        }


# Singleton
_jobs_loader = None

def get_jobs_loader():
    """Get or create jobs loader singleton."""
    global _jobs_loader
    if _jobs_loader is None:
        _jobs_loader = JobsLoader()
    return _jobs_loader
