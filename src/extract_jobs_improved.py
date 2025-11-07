"""Improved job extractor."""
import instructor
from openai import OpenAI
from pathlib import Path
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

class JobOpening(BaseModel):
    title: str
    department: str = "General"
    location: str = "Not specified"
    type: str = "Full-time"
    description: Optional[str] = None

class JobsData(BaseModel):
    company_id: str
    total_openings: int
    departments: List[str] = Field(default_factory=list)
    jobs: List[JobOpening] = Field(default_factory=list)
    hiring_focus: Optional[str] = None
    is_actively_hiring: bool = True


class ImprovedJobExtractor:
    def __init__(self):
        self.client = instructor.from_openai(OpenAI(api_key=os.getenv('OPENAI_API_KEY')))
        self.model = "gpt-4o-mini"
        self.data_dir = Path("data/raw")
    
    def extract_jobs(self, company_id: str) -> Optional[JobsData]:
        print(f"Job extraction for {company_id}...", end=" ")
        
        company_dir = self.data_dir / company_id
        if not company_dir.exists():
            print("No data")
            return None
        
        latest_run = sorted(company_dir.iterdir())[-1]
        careers_file = latest_run / "careers.txt"
        
        if not careers_file.exists():
            print("No careers page")
            return None
        
        careers_text = careers_file.read_text(encoding='utf-8')
        
        if len(careers_text) < 200:
            print("Too short")
            return None
        
        try:
            prompt = f"""Extract ALL job openings from this careers page.

Company: {company_id}

Text:
{careers_text[:12000]}

Extract every job title, department, and role mentioned. If departments are listed, infer typical roles.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                response_model=JobsData,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract all job openings. Be thorough."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2500
            )
            
            output_dir = Path("data/jobs_improved")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{company_id}.json"
            output_file.write_text(response.model_dump_json(indent=2))
            
            print(f"Found {response.total_openings} jobs")
            return response
            
        except Exception as e:
            print(f"Error: {e}")
            return None


def extract_all_improved():
    print("Starting improved job extraction...")
    extractor = ImprovedJobExtractor()
    
    raw_dir = Path("data/raw")
    companies = sorted([d.name for d in raw_dir.iterdir() if d.is_dir()])
    
    print(f"Processing {len(companies)} companies\n")
    
    results = []
    for company_id in companies:
        jobs_data = extractor.extract_jobs(company_id)
        if jobs_data:
            results.append({'company_id': company_id, 'total_openings': jobs_data.total_openings})
        else:
            results.append({'company_id': company_id, 'total_openings': 0})
    
    total = sum(r['total_openings'] for r in results)
    print(f"\nTotal jobs found: {total}")
    
    return results


if __name__ == "__main__":
    extract_all_improved()