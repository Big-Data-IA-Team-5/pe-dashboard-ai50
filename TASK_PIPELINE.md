# Pipeline & Embedding Engineer - Task Guide
**Role**: Data Ingestion, Airflow, Vector DB, Structured Extraction  
**Your Responsibility**: 33% of the project (Most Labs!)

---

## 📂 Current Folder Structure (What You Have)

```
pe-dashboard-ai50/
├── data/
│   ├── forbes_ai50_seed.json    🔴 PLACEHOLDER - YOU MUST POPULATE
│   ├── starter_payload.json     ✅ Example structure (REFERENCE)
│   └── raw/                     🔴 YOU WILL CREATE
│       └── <company_id>/
│           └── YYYY-MM-DD/
│               ├── homepage.html
│               ├── about.html
│               └── metadata.json
├── dags/
│   ├── ai50_full_ingest_dag.py  🟡 Skeleton EXISTS - YOU MUST IMPLEMENT
│   └── ai50_daily_refresh_dag.py 🟡 Skeleton EXISTS - YOU MUST IMPLEMENT
├── src/
│   ├── models.py                ✅ Complete Pydantic models (USE THESE)
│   ├── structured_pipeline.py   🟡 Has load function (YOU ADD MORE)
│   └── rag_pipeline.py         🟡 Has stub (YOU REPLACE)
└── requirements.txt             🟡 Need to add: beautifulsoup4, instructor, chromadb
```

---

## 🎯 Your Tasks & What's Left to Do

### ✅ What You Already Have (Starter Code)
- **File**: `dags/ai50_full_ingest_dag.py` - Skeleton with placeholder tasks
- **File**: `dags/ai50_daily_refresh_dag.py` - Skeleton with placeholder tasks
- **File**: `src/models.py` - Complete Pydantic models ✅
- **File**: `data/forbes_ai50_seed.json` - Schema only (1 placeholder company)

### 🔴 What You Need to Build (8 Labs!)

---

## TASK 1: Populate Forbes AI 50 Seed Data (Lab 0)
**File**: `data/forbes_ai50_seed.json`  
**Location**: Overwrite existing placeholder  
**Estimated Time**: 2 hours

### What to Do:
1. Go to https://www.forbes.com/lists/ai50/
2. Scrape or manually collect all 50 companies
3. For each company, get:
   - company_name
   - website
   - linkedin (if available)
   - hq_city, hq_country
   - category (e.g., "Enterprise AI", "Healthcare AI")
   - company_id (generate UUID)

### Output Format:
```json
[
  {
    "company_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "company_name": "Scale AI",
    "website": "https://scale.com",
    "linkedin": "https://www.linkedin.com/company/scaleai/",
    "hq_city": "San Francisco",
    "hq_state": "CA",
    "hq_country": "United States",
    "category": "Data Labeling"
  },
  {
    "company_id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
    "company_name": "Cohere",
    "website": "https://cohere.com",
    "linkedin": "https://www.linkedin.com/company/cohere-ai/",
    "hq_city": "Toronto",
    "hq_state": "ON",
    "hq_country": "Canada",
    "category": "LLM Platform"
  }
  // ... 48 more companies
]
```

### Quick Script to Help:
```python
# scripts/scrape_forbes_ai50.py
import requests
from bs4 import BeautifulSoup
import json
import uuid

def scrape_forbes_ai50():
    url = "https://www.forbes.com/lists/ai50/"
    # Note: Forbes may require JavaScript, consider using Playwright
    
    companies = []
    
    # TODO: Implement scraping logic
    # For now, manual entry is OK
    
    return companies

if __name__ == "__main__":
    companies = scrape_forbes_ai50()
    
    # Generate UUIDs
    for company in companies:
        company["company_id"] = str(uuid.uuid4())
    
    with open("data/forbes_ai50_seed.json", "w") as f:
        json.dump(companies, f, indent=2)
    
    print(f"Scraped {len(companies)} companies")
```

**Dependencies**: None - this is the foundation!

**Deliverable**: `data/forbes_ai50_seed.json` with all 50 companies

---

## TASK 2: Build Web Scraper (Lab 1)
**File**: Create new file `src/scraper.py`  
**Location**: New file in `src/`  
**Estimated Time**: 6 hours

### What to Create:
```python
# src/scraper.py
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Optional
import time
import hashlib

class CompanyScraper:
    """Scraper for company websites."""
    
    def __init__(self, data_dir: Path = Path("data/raw")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def scrape_company(self, company: Dict) -> Dict:
        """
        Scrape all pages for a company.
        
        Args:
            company: Dict with company_id, company_name, website
            
        Returns:
            Scraping results with status
        """
        company_id = company["company_id"]
        company_name = company["company_name"]
        base_url = company["website"]
        
        print(f"Scraping {company_name}...")
        
        # Create folder structure
        today = datetime.now().strftime("%Y-%m-%d")
        company_folder = self.data_dir / company_id / today
        company_folder.mkdir(parents=True, exist_ok=True)
        
        # Pages to scrape
        pages_to_scrape = [
            ("homepage", ""),
            ("about", "/about"),
            ("product", "/product"),
            ("platform", "/platform"),
            ("careers", "/careers"),
            ("jobs", "/jobs"),
            ("blog", "/blog"),
            ("news", "/news")
        ]
        
        scraped_pages = []
        
        for page_name, path in pages_to_scrape:
            try:
                url = f"{base_url.rstrip('/')}{path}"
                result = self._scrape_page(url, page_name, company_folder)
                
                if result:
                    scraped_pages.append(result)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"  Error scraping {page_name}: {e}")
        
        # Save metadata
        metadata = {
            "company_id": company_id,
            "company_name": company_name,
            "base_url": base_url,
            "scraped_at": datetime.now().isoformat(),
            "pages_scraped": len(scraped_pages),
            "pages": scraped_pages
        }
        
        (company_folder / "metadata.json").write_text(json.dumps(metadata, indent=2))
        
        return {
            "company_id": company_id,
            "company_name": company_name,
            "status": "success" if scraped_pages else "failed",
            "pages_scraped": len(scraped_pages),
            "folder": str(company_folder)
        }
    
    def _scrape_page(self, url: str, page_name: str, output_folder: Path) -> Optional[Dict]:
        """Scrape single page."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                return None  # Page doesn't exist
            
            response.raise_for_status()
            
            # Save raw HTML
            html_file = output_folder / f"{page_name}.html"
            html_file.write_text(response.text, encoding='utf-8')
            
            # Extract clean text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            # Save clean text
            text_file = output_folder / f"{page_name}.txt"
            text_file.write_text(text, encoding='utf-8')
            
            # Calculate hash for change detection
            content_hash = hashlib.sha256(response.content).hexdigest()
            
            print(f"  ✓ Scraped {page_name} ({len(text)} chars)")
            
            return {
                "page_name": page_name,
                "url": url,
                "status_code": response.status_code,
                "content_length": len(text),
                "hash": content_hash,
                "html_file": html_file.name,
                "text_file": text_file.name
            }
            
        except requests.RequestException as e:
            print(f"  ✗ Failed {page_name}: {e}")
            return None


def scrape_all_companies(companies_file: Path = Path("data/forbes_ai50_seed.json")) -> list:
    """Scrape all companies from seed file."""
    companies = json.loads(companies_file.read_text())
    
    scraper = CompanyScraper()
    results = []
    
    for company in companies:
        try:
            result = scraper.scrape_company(company)
            results.append(result)
        except Exception as e:
            print(f"Failed to scrape {company['company_name']}: {e}")
            results.append({
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "status": "error",
                "error": str(e)
            })
    
    return results


if __name__ == "__main__":
    results = scrape_all_companies()
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\nCompleted: {success_count}/{len(results)} companies scraped successfully")
```

### Add to `requirements.txt`:
```txt
beautifulsoup4>=4.12.0
lxml>=4.9.0
requests>=2.32.3
```

### Install:
```bash
pip install beautifulsoup4 lxml requests
```

### Test:
```bash
# Test on one company first
python -c "
from src.scraper import CompanyScraper
import json

companies = json.load(open('data/forbes_ai50_seed.json'))
scraper = CompanyScraper()
result = scraper.scrape_company(companies[0])
print(result)
"
```

**Dependencies**: Need TASK 1 completed (forbes_ai50_seed.json)

**Deliverable**: 
- `src/scraper.py` working
- `data/raw/<company_id>/YYYY-MM-DD/` folders with HTML and TXT files

---

## TASK 3: Full Ingestion Airflow DAG (Lab 2)
**File**: `dags/ai50_full_ingest_dag.py`  
**Location**: Replace existing skeleton  
**Estimated Time**: 4 hours

### What to Create:
```python
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from pathlib import Path
import json
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_company_list(**context):
    """Load Forbes AI 50 companies."""
    seed_path = DATA_DIR / "forbes_ai50_seed.json"
    companies = json.loads(seed_path.read_text())
    
    print(f"Loaded {len(companies)} companies")
    
    # Push to XCom
    context['ti'].xcom_push(key='companies', value=companies)
    
    return companies


def scrape_company(company_data: dict, **context):
    """Scrape a single company."""
    from src.scraper import CompanyScraper
    
    scraper = CompanyScraper(data_dir=DATA_DIR / "raw")
    result = scraper.scrape_company(company_data)
    
    return result


def scrape_all_companies(**context):
    """Scrape all companies."""
    from src.scraper import scrape_all_companies
    
    results = scrape_all_companies(DATA_DIR / "forbes_ai50_seed.json")
    
    # Save log
    log_file = DATA_DIR / "raw" / "full_ingest_log.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(json.dumps(results, indent=2))
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    print(f"Scraped {success_count}/{len(results)} companies successfully")
    
    return results


def store_metadata(**context):
    """Store aggregated metadata."""
    ti = context['ti']
    
    # This is where you'd upload to GCS/S3
    # For now, just log
    print("Metadata stored in data/raw/full_ingest_log.json")


with DAG(
    dag_id="ai50_full_ingest_dag",
    start_date=datetime(2025, 10, 31),
    schedule="@once",
    catchup=False,
    tags=["ai50", "orbit", "full-load"],
    description="Full ingestion of all Forbes AI 50 companies"
) as dag:

    load_task = PythonOperator(
        task_id="load_company_list",
        python_callable=load_company_list,
    )

    scrape_task = PythonOperator(
        task_id="scrape_all_companies",
        python_callable=scrape_all_companies,
    )

    store_task = PythonOperator(
        task_id="store_metadata",
        python_callable=store_metadata,
    )

    load_task >> scrape_task >> store_task
```

### Test Airflow Locally:
```bash
# Option 1: Airflow standalone
export AIRFLOW_HOME=~/airflow
airflow standalone

# Option 2: Docker (recommended)
# Use docker-compose.airflow.yml (you may need to create this)

# Visit http://localhost:8080
# Enable and trigger ai50_full_ingest_dag
```

**Dependencies**: Need TASK 1 & 2 completed

**Deliverable**: Working DAG that scrapes all 50 companies

---

## TASK 4: Daily Refresh DAG (Lab 3)
**File**: `dags/ai50_daily_refresh_dag.py`  
**Location**: Replace existing skeleton  
**Estimated Time**: 3 hours

### What to Create:
```python
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path
import json
import hashlib

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def detect_changed_companies(**context):
    """Detect which companies have changed pages."""
    seed_path = DATA_DIR / "forbes_ai50_seed.json"
    companies = json.loads(seed_path.read_text())
    
    changed = []
    
    for company in companies:
        company_id = company["company_id"]
        company_folder = DATA_DIR / "raw" / company_id
        
        if not company_folder.exists():
            changed.append(company)  # New company
            continue
        
        # Check if we should refresh (refresh key pages every day)
        changed.append(company)
    
    print(f"Found {len(changed)} companies to refresh")
    context['ti'].xcom_push(key='changed_companies', value=changed)
    
    return changed


def refresh_company_pages(**context):
    """Refresh key pages for changed companies."""
    from src.scraper import CompanyScraper
    
    ti = context['ti']
    companies = ti.xcom_pull(key='changed_companies', task_ids='detect_changed')
    
    scraper = CompanyScraper(data_dir=DATA_DIR / "raw")
    results = []
    
    # Only scrape key signal pages
    for company in companies[:10]:  # Limit to 10 per day to avoid rate limits
        try:
            result = scraper.scrape_company(company)
            results.append(result)
        except Exception as e:
            print(f"Error: {e}")
    
    # Save log
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = DATA_DIR / "raw" / f"daily_refresh_{today}.json"
    log_file.write_text(json.dumps(results, indent=2))
    
    return results


with DAG(
    dag_id="ai50_daily_refresh_dag",
    start_date=datetime(2025, 10, 31),
    schedule="0 3 * * *",  # 3 AM daily
    catchup=False,
    tags=["ai50", "orbit", "daily"],
    description="Daily refresh of Forbes AI 50 company data"
) as dag:

    detect_task = PythonOperator(
        task_id="detect_changed",
        python_callable=detect_changed_companies,
    )

    refresh_task = PythonOperator(
        task_id="refresh_pages",
        python_callable=refresh_company_pages,
    )

    detect_task >> refresh_task
```

**Dependencies**: Need TASK 2 & 3 completed

**Deliverable**: Daily DAG that refreshes changed companies

---

## TASK 5: Structured Extraction with Instructor (Lab 5)
**File**: Create new file `src/extractor.py`  
**Location**: New file in `src/`  
**Estimated Time**: 8 hours

### What to Create:
```python
# src/extractor.py
import instructor
from openai import OpenAI
import os
from pathlib import Path
from typing import List, Optional
from datetime import date, datetime
import json

from .models import (
    Company, Event, Snapshot, Product,
    Leadership, Visibility, Provenance
)

class DataExtractor:
    """Extract structured data from scraped pages using instructor."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required")
        
        # Patch OpenAI client with instructor
        self.client = instructor.from_openai(OpenAI(api_key=self.api_key))
    
    def extract_company_info(
        self,
        company_name: str,
        homepage_text: str,
        about_text: str,
        source_urls: dict
    ) -> Company:
        """Extract Company model from homepage and about page."""
        
        combined_text = f"""
Company: {company_name}

Homepage:
{homepage_text[:2000]}

About Page:
{about_text[:2000]}
"""
        
        prompt = f"""Extract company information from the following text.
Fill in as many fields as possible from the Company model.
Use "Not disclosed" for missing information.

{combined_text}
"""
        
        try:
            company = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_model=Company,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Extract accurate company information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Add provenance
            company.provenance = [
                Provenance(
                    source_url=source_urls.get("homepage", ""),
                    crawled_at=datetime.now().isoformat(),
                    snippet=homepage_text[:200]
                )
            ]
            
            company.as_of = date.today()
            
            return company
            
        except Exception as e:
            print(f"Error extracting company info: {e}")
            return None
    
    def extract_events(
        self,
        company_id: str,
        blog_text: str,
        news_text: str,
        source_urls: dict
    ) -> List[Event]:
        """Extract Event models from blog/news."""
        
        combined_text = f"""
Blog:
{blog_text[:3000]}

News:
{news_text[:3000]}
"""
        
        prompt = f"""Extract all significant events mentioned in the text.
Focus on: funding rounds, partnerships, product launches, leadership changes.

{combined_text}
"""
        
        try:
            # Note: instructor can extract lists directly
            events = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_model=List[Event],
                messages=[
                    {"role": "system", "content": "Extract all events as Event objects."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Set company_id and provenance
            for event in events:
                event.company_id = company_id
                event.provenance = [
                    Provenance(
                        source_url=source_urls.get("blog", ""),
                        crawled_at=datetime.now().isoformat()
                    )
                ]
            
            return events
            
        except Exception as e:
            print(f"Error extracting events: {e}")
            return []
    
    def extract_snapshot(
        self,
        company_id: str,
        careers_text: str,
        source_url: str
    ) -> Optional[Snapshot]:
        """Extract Snapshot model from careers page."""
        
        prompt = f"""Extract hiring and company snapshot data from this careers page:

{careers_text[:2000]}
"""
        
        try:
            snapshot = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_model=Snapshot,
                messages=[
                    {"role": "system", "content": "Extract hiring metrics and job opening data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            snapshot.company_id = company_id
            snapshot.as_of = date.today()
            snapshot.provenance = [
                Provenance(
                    source_url=source_url,
                    crawled_at=datetime.now().isoformat(),
                    snippet=careers_text[:200]
                )
            ]
            
            return snapshot
            
        except Exception as e:
            print(f"Error extracting snapshot: {e}")
            return None
    
    def extract_products(
        self,
        company_id: str,
        product_text: str,
        source_url: str
    ) -> List[Product]:
        """Extract Product models from product page."""
        
        prompt = f"""Extract all products/services from this page:

{product_text[:2000]}
"""
        
        try:
            products = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_model=List[Product],
                messages=[
                    {"role": "system", "content": "Extract product information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            for product in products:
                product.company_id = company_id
                product.provenance = [
                    Provenance(
                        source_url=source_url,
                        crawled_at=datetime.now().isoformat()
                    )
                ]
            
            return products
            
        except Exception as e:
            print(f"Error extracting products: {e}")
            return []
    
    def extract_all(self, company_data: dict, scraped_folder: Path) -> dict:
        """
        Extract all structured data for a company.
        
        Args:
            company_data: Dict with company_id, company_name, etc.
            scraped_folder: Path to folder with scraped .txt files
            
        Returns:
            Dict with all extracted models
        """
        company_id = company_data["company_id"]
        company_name = company_data["company_name"]
        
        print(f"Extracting structured data for {company_name}...")
        
        # Load scraped text files
        texts = {}
        source_urls = {}
        
        for txt_file in scraped_folder.glob("*.txt"):
            page_name = txt_file.stem
            texts[page_name] = txt_file.read_text()
            source_urls[page_name] = company_data.get("website", "") + f"/{page_name}"
        
        # Extract each model
        company_record = self.extract_company_info(
            company_name,
            texts.get("homepage", ""),
            texts.get("about", ""),
            source_urls
        )
        
        events = self.extract_events(
            company_id,
            texts.get("blog", ""),
            texts.get("news", ""),
            source_urls
        )
        
        snapshot = self.extract_snapshot(
            company_id,
            texts.get("careers", texts.get("jobs", "")),
            source_urls.get("careers", source_urls.get("jobs", ""))
        )
        
        products = self.extract_products(
            company_id,
            texts.get("product", texts.get("platform", "")),
            source_urls.get("product", source_urls.get("platform", ""))
        )
        
        # Combine into structured format
        result = {
            "company_record": company_record.model_dump(mode='json') if company_record else None,
            "events": [e.model_dump(mode='json') for e in events],
            "snapshots": [snapshot.model_dump(mode='json')] if snapshot else [],
            "products": [p.model_dump(mode='json') for p in products],
            "leadership": [],  # TODO: implement if needed
            "visibility": []   # TODO: implement if needed
        }
        
        return result


def extract_company(company_data: dict, scraped_folder: Path, output_folder: Path):
    """Extract and save structured data for one company."""
    extractor = DataExtractor()
    
    result = extractor.extract_all(company_data, scraped_folder)
    
    # Save to data/structured/
    output_file = output_folder / f"{company_data['company_id']}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(result, indent=2))
    
    print(f"Saved structured data to {output_file}")
    
    return result


if __name__ == "__main__":
    # Test on one company
    companies = json.loads(Path("data/forbes_ai50_seed.json").read_text())
    company = companies[0]
    
    # Find latest scraped folder
    import glob
    company_folders = glob.glob(f"data/raw/{company['company_id']}/*")
    if company_folders:
        latest_folder = Path(sorted(company_folders)[-1])
        
        extract_company(
            company,
            latest_folder,
            Path("data/structured")
        )
```

### Add to `requirements.txt`:
```txt
instructor>=0.4.0
openai>=1.12.0
```

### Install:
```bash
pip install instructor openai
```

**Dependencies**: 
- Need TASK 2 completed (scraped data)
- Need OpenAI API key

**Deliverable**: 
- `src/extractor.py` working
- `data/structured/<company_id>.json` files

---

## TASK 6: Payload Assembly (Lab 6)
**File**: `src/structured_pipeline.py`  
**Location**: Add to existing file  
**Estimated Time**: 3 hours

### What to Add:
```python
# Add to src/structured_pipeline.py

from pathlib import Path
from typing import Optional
import json
from .models import Payload

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
STRUCTURED_DIR = DATA_DIR / "structured"
PAYLOAD_DIR = DATA_DIR / "payloads"

def load_payload(company_id: str) -> Optional[Payload]:
    """Load payload from file (existing function)."""
    fp = PAYLOAD_DIR / f"{company_id}.json"
    if not fp.exists():
        starter = DATA_DIR / "starter_payload.json"
        if starter.exists():
            return Payload.model_validate_json(starter.read_text())
        return None
    return Payload.model_validate_json(fp.read_text())


def assemble_payload(company_id: str) -> Optional[Payload]:
    """
    Assemble complete Payload from structured extraction.
    
    Combines all extracted data into a single Payload object.
    """
    structured_file = STRUCTURED_DIR / f"{company_id}.json"
    
    if not structured_file.exists():
        print(f"No structured data found for {company_id}")
        return None
    
    # Load extracted data
    data = json.loads(structured_file.read_text())
    
    # Build Payload
    payload_dict = {
        "company_record": data.get("company_record"),
        "events": data.get("events", []),
        "snapshots": data.get("snapshots", []),
        "products": data.get("products", []),
        "leadership": data.get("leadership", []),
        "visibility": data.get("visibility", []),
        "notes": "Auto-generated from structured extraction",
        "provenance_policy": "Use only the sources you scraped. If a field is missing, write 'Not disclosed.' Do not infer valuation."
    }
    
    # Validate with Pydantic
    try:
        payload = Payload.model_validate(payload_dict)
        
        # Save to payloads/
        PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
        payload_file = PAYLOAD_DIR / f"{company_id}.json"
        payload_file.write_text(payload.model_dump_json(indent=2))
        
        print(f"✓ Assembled payload for {payload.company_record.legal_name}")
        
        return payload
        
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return None


def assemble_all_payloads():
    """Assemble payloads for all companies with structured data."""
    results = []
    
    for structured_file in STRUCTURED_DIR.glob("*.json"):
        company_id = structured_file.stem
        
        try:
            payload = assemble_payload(company_id)
            if payload:
                results.append({
                    "company_id": company_id,
                    "company_name": payload.company_record.legal_name,
                    "status": "success"
                })
        except Exception as e:
            print(f"Error assembling {company_id}: {e}")
            results.append({
                "company_id": company_id,
                "status": "error",
                "error": str(e)
            })
    
    print(f"\nAssembled {len([r for r in results if r['status']=='success'])}/{len(results)} payloads")
    
    return results


if __name__ == "__main__":
    results = assemble_all_payloads()
```

**Dependencies**: Need TASK 5 completed

**Deliverable**: `data/payloads/<company_id>.json` files ready for Backend Engineer

---

## TASK 7: Vector DB & RAG (Lab 4)
**File**: Create new file `src/vector_db.py`  
**Location**: New file in `src/`  
**Estimated Time**: 4 hours

### What to Create:
```python
# src/vector_db.py
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict
import json
from sentence_transformers import SentenceTransformer

class VectorDB:
    """Vector database for RAG."""
    
    def __init__(self, persist_directory: str = "data/chromadb"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="company_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Use local embeddings (no API key needed)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def index_company(self, company_id: str, company_name: str, scraped_folder: Path):
        """Index all scraped documents for a company."""
        print(f"Indexing {company_name}...")
        
        documents = []
        metadatas = []
        ids = []
        
        # Load all text files
        for txt_file in scraped_folder.glob("*.txt"):
            text = txt_file.read_text()
            page_name = txt_file.stem
            
            # Chunk the text
            chunks = self.chunk_text(text)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{company_id}_{page_name}_{i}"
                
                documents.append(chunk)
                metadatas.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "page_name": page_name,
                    "chunk_index": i,
                    "source_url": f"https://{company_name.lower().replace(' ', '')}.com/{page_name}"
                })
                ids.append(chunk_id)
        
        if documents:
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"  Indexed {len(documents)} chunks")
    
    def retrieve_context(
        self,
        company_name: str,
        query: str = "",
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant context for a company.
        
        This is the function Backend Engineer needs!
        
        Args:
            company_name: Company to search for
            query: Optional query (if empty, returns general company info)
            top_k: Number of chunks to return
            
        Returns:
            List of dicts with 'source_url', 'text', 'score'
        """
        if not query:
            query = f"Tell me about {company_name}"
        
        # Search
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"company_name": company_name}
        )
        
        if not results['documents'][0]:
            return []
        
        # Format results
        chunks = []
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            chunks.append({
                "source_url": metadata.get("source_url", ""),
                "text": doc,
                "score": 1 - distance,  # Convert distance to similarity score
                "page_name": metadata.get("page_name", "")
            })
        
        return chunks
    
    def index_all_companies(self, companies_file: Path, raw_data_dir: Path):
        """Index all companies."""
        companies = json.loads(companies_file.read_text())
        
        for company in companies:
            company_id = company["company_id"]
            company_name = company["company_name"]
            
            # Find latest scraped folder
            company_folders = list((raw_data_dir / company_id).glob("*"))
            if company_folders:
                latest_folder = sorted(company_folders)[-1]
                self.index_company(company_id, company_name, latest_folder)


# Export the function Backend Engineer needs
def retrieve_context(company_name: str, query: str = "", top_k: int = 5) -> List[Dict]:
    """
    Retrieve relevant context from vector DB.
    
    This is the interface for Backend Engineer's RAG pipeline.
    """
    db = VectorDB()
    return db.retrieve_context(company_name, query, top_k)


if __name__ == "__main__":
    # Build the index
    db = VectorDB()
    db.index_all_companies(
        Path("data/forbes_ai50_seed.json"),
        Path("data/raw")
    )
    
    # Test retrieval
    results = retrieve_context("ExampleAI", "funding", top_k=3)
    print(json.dumps(results, indent=2))
```

### Add to `requirements.txt`:
```txt
chromadb>=0.4.0
sentence-transformers>=2.2.0
```

### Install:
```bash
pip install chromadb sentence-transformers
```

**Dependencies**: Need TASK 2 completed (scraped data)

**Deliverable**: 
- `src/vector_db.py` with `retrieve_context()` function
- Vector DB indexed with all companies

---

## TASK 8: DAG Integration (Lab 11)
**File**: Update both DAG files  
**Location**: `dags/ai50_full_ingest_dag.py` and `dags/ai50_daily_refresh_dag.py`  
**Estimated Time**: 3 hours

### Add to Full Ingest DAG:
```python
# Add after scrape_all_companies task

def extract_all_structured(**context):
    """Extract structured data from all scraped companies."""
    from src.extractor import extract_company
    import json
    
    companies = json.loads((DATA_DIR / "forbes_ai50_seed.json").read_text())
    
    for company in companies:
        company_id = company["company_id"]
        
        # Find latest scraped folder
        company_folders = list((DATA_DIR / "raw" / company_id).glob("*"))
        if company_folders:
            latest_folder = sorted(company_folders)[-1]
            
            extract_company(
                company,
                latest_folder,
                DATA_DIR / "structured"
            )


def assemble_all(**context):
    """Assemble payloads."""
    from src.structured_pipeline import assemble_all_payloads
    
    results = assemble_all_payloads()
    return results


def index_vector_db(**context):
    """Index all companies in vector DB."""
    from src.vector_db import VectorDB
    
    db = VectorDB()
    db.index_all_companies(
        DATA_DIR / "forbes_ai50_seed.json",
        DATA_DIR / "raw"
    )


# Add tasks to DAG
extract_task = PythonOperator(
    task_id="extract_structured",
    python_callable=extract_all_structured
)

assemble_task = PythonOperator(
    task_id="assemble_payloads",
    python_callable=assemble_all
)

index_task = PythonOperator(
    task_id="index_vector_db",
    python_callable=index_vector_db
)

# Update task dependencies
load_task >> scrape_task >> extract_task >> assemble_task >> index_task >> store_task
```

**Dependencies**: All previous tasks

**Deliverable**: End-to-end DAG that produces payloads and vector DB

---

## 📦 Dependencies Summary

### Add to `requirements.txt`:
```txt
# Web scraping
beautifulsoup4>=4.12.0
lxml>=4.9.0
requests>=2.32.3

# LLM & Structured extraction
openai>=1.12.0
instructor>=0.4.0
python-dotenv>=1.0.0

# Vector DB
chromadb>=0.4.0
sentence-transformers>=2.2.0

# Airflow (if running locally)
apache-airflow>=2.7.0
```

### Install All:
```bash
pip install beautifulsoup4 lxml requests openai instructor python-dotenv chromadb sentence-transformers
```

---

## 🔗 Integration Points

### What Backend Engineer Needs from You:
1. **Vector DB Retrieval Function**:
   ```python
   from src.vector_db import retrieve_context
   
   chunks = retrieve_context("Company Name", "funding", top_k=5)
   # Returns: [{"source_url": ..., "text": ..., "score": ...}, ...]
   ```

2. **Payload Files**:
   - Location: `data/payloads/<company_id>.json`
   - Format: Must match `Payload` Pydantic model
   - Minimum: 5 companies for evaluation

3. **Company ID Mapping**:
   - Include `company_id` in `forbes_ai50_seed.json`

### What Frontend Engineer Needs from You:
1. **Populated Seed File**: `data/forbes_ai50_seed.json` with 50 companies
2. **Payload Availability**: At least 5 complete payloads

---

## ✅ Deliverables Checklist

- [ ] `data/forbes_ai50_seed.json` - All 50 companies
- [ ] `src/scraper.py` - Web scraper
- [ ] `data/raw/<company_id>/YYYY-MM-DD/` - Scraped HTML & TXT
- [ ] `dags/ai50_full_ingest_dag.py` - Full ingestion DAG
- [ ] `dags/ai50_daily_refresh_dag.py` - Daily refresh DAG
- [ ] `src/extractor.py` - Structured extraction
- [ ] `data/structured/<company_id>.json` - Extracted data
- [ ] `src/structured_pipeline.py` - Payload assembly
- [ ] `data/payloads/<company_id>.json` - Complete payloads (5+ companies)
- [ ] `src/vector_db.py` - Vector DB with `retrieve_context()`
- [ ] ChromaDB indexed with all companies
- [ ] End-to-end DAG integration
- [ ] Documentation of data pipeline

---

## 🚀 Getting Started (Your First Steps)

### Day 1:
```bash
# 1. Get OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# 2. Install dependencies
pip install beautifulsoup4 lxml requests instructor chromadb sentence-transformers

# 3. Create feature branch
git checkout -b feature/data-pipeline
```

### Day 2-3:
- TASK 1: Populate Forbes AI 50 seed (manual or scrape)
- TASK 2: Build web scraper
- Test on 2-3 companies

### Day 4:
- TASK 3: Full ingestion DAG
- Run scraper on all 50 companies

### Day 5-7:
- TASK 5: Structured extraction with instructor
- Test on 5 companies
- TASK 6: Assemble payloads

### Day 8:
- TASK 7: Vector DB
- Index all companies

### Day 9:
- TASK 4: Daily refresh DAG
- TASK 8: DAG integration

### Day 10:
- Testing & documentation
- Handoff to Backend Engineer

---

## 💡 Tips for Success

1. **Start Small**: Test on 2-3 companies before running all 50
2. **Handle Errors Gracefully**: Many company websites will fail
3. **Rate Limiting**: Add delays between requests
4. **Parallel Processing**: Use Airflow dynamic task mapping for scaling
5. **Monitor Costs**: OpenAI API costs can add up (use GPT-3.5 for testing)

Good luck! 🚀
