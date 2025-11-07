"""Vector Database with GCS integration."""
import os
from pathlib import Path
from google.cloud import storage
import tempfile
import shutil
from src.vector_db import VectorDatabase


class VectorDatabaseGCS:
    """Vector Database that loads from GCS."""
    
    def __init__(self, use_gcs: bool = None):
        """
        Initialize Vector DB from GCS or local.
        
        Args:
            use_gcs: If True, download from GCS. If None, auto-detect from env.
        """
        self.bucket_name = "us-central1-pe-airflow-env-2825d831-bucket"
        self.gcs_path = "data/vector_db/"
        self.local_path = Path("data/vector_db")
        
        # Auto-detect environment
        if use_gcs is None:
            use_gcs = os.getenv("ENVIRONMENT") == "production" or os.getenv("VECTOR_DB_USE_GCS", "").lower() == "true"
        
        if use_gcs:
            print("📥 Loading ChromaDB from GCS...")
            self._download_from_gcs()
        else:
            print("📂 Using local ChromaDB...")
        
        # Initialize vector DB (P1's code)
        self.vdb = VectorDatabase()
        print(f"✓ Vector DB ready: {self.vdb.get_stats()}")
    
    def _download_from_gcs(self):
        """Download ChromaDB from GCS to local temp directory."""
        try:
            # Set up GCS client
            key_file = os.getenv("GCP_SERVICE_ACCOUNT_KEY", "./gcp-service-account-key.json")
            
            if Path(key_file).exists():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file
            
            client = storage.Client(project="pe-dashboard-ai50")
            bucket = client.bucket(self.bucket_name)
            
            # Create local directory
            self.local_path.mkdir(parents=True, exist_ok=True)
            
            # Download all files from GCS
            blobs = bucket.list_blobs(prefix=self.gcs_path)
            
            downloaded = 0
            for blob in blobs:
                # Get relative path
                relative_path = blob.name[len(self.gcs_path):]
                if not relative_path:
                    continue
                
                # Local destination
                local_file = self.local_path / relative_path
                local_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Download
                blob.download_to_filename(str(local_file))
                downloaded += 1
            
            print(f"  ✓ Downloaded {downloaded} files from GCS")
            
        except Exception as e:
            print(f"  ⚠️  GCS download failed: {e}")
            print(f"  Falling back to local vector DB if available")
    
    def search(self, company_id: str, query: str, k: int = 5):
        """Search vector DB (delegates to P1's implementation)."""
        return self.vdb.search(company_id, query, k)
    
    def get_stats(self):
        """Get DB stats (delegates to P1's implementation)."""
        return self.vdb.get_stats()


# Singleton
_vdb_gcs = None

def get_vector_db_gcs():
    """Get or create Vector DB GCS singleton."""
    global _vdb_gcs
    if _vdb_gcs is None:
        _vdb_gcs = VectorDatabaseGCS()
    return _vdb_gcs
