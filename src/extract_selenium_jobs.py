"""Extract jobs from Selenium-scraped pages."""
import instructor
from openai import OpenAI
from pathlib import Path
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class JobOpening(BaseModel):
    title: str
    department: str = "General"
    location: str = "Not specified"
    type: str = "Full-time"

class JobsData(BaseModel):
    company_id: str
    total_openings: int
    departments: List[str] = Field(default_factory=list)
    jobs: List[JobOpening] = Field(default_factory=list)
    hiring_focus: Optional[str] = None

class SeleniumJobExtractor:
    def __init__(self):
        self.client = instructor.from_openai(OpenAI())
        self.model = "gpt-4o-mini"
    
    def extract_jobs(self, company_id: str) -> Optional[JobsData]:
        print(f"💼 {company_id}...", end=" ")
        
        careers_file = Path(f"data/careers_selenium/{company_id}/page.txt")
        
        if not careers_file.exists():
            print("No page")
            return None
        
        text = careers_file.read_text(encoding='utf-8')
        
        if len(text) < 500:
            print("Too short")
            return None
        
        try:
            # Extract with increased token limit
            prompt = f"""Extract ALL job listings from this careers page.

Company: {company_id}

Look for:
- Job titles (Software Engineer, Product Manager, etc.)
- Departments
- Locations  
- Any role names mentioned

Text (first 15000 chars):
{text[:15000]}

Extract EVERY job you can find. If you see department names, infer typical roles.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                response_model=JobsData,
                messages=[
                    {"role": "system", "content": "Extract all jobs. Be thorough."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000  # Increased for companies with many jobs
            )
            
            # Save
            output_dir = Path("data/jobs_final")
            output_dir.mkdir(exist_ok=True)
            (output_dir / f"{company_id}.json").write_text(response.model_dump_json(indent=2))
            
            print(f"✅ {response.total_openings} jobs")
            return response
            
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return None

def extract_all_selenium_jobs():
    print("🚀 Extracting jobs from Selenium pages\n")
    
    extractor = SeleniumJobExtractor()
    careers_dir = Path("data/careers_selenium")
    
    companies = sorted([d.name for d in careers_dir.iterdir() if d.is_dir()])
    print(f"Processing {len(companies)} companies\n")
    
    results = []
    for company_id in companies:
        jobs = extractor.extract_jobs(company_id)
        if jobs:
            results.append({'company_id': company_id, 'total': jobs.total_openings})
        else:
            results.append({'company_id': company_id, 'total': 0})
    
    total = sum(r['total'] for r in results)
    print(f"\n✅ Total jobs extracted: {total}")
    
    return results

if __name__ == "__main__":
    extract_all_selenium_jobs()