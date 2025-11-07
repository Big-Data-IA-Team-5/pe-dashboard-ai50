"""Extract structured data using Instructor + OpenAI."""
import instructor
from openai import OpenAI
from pathlib import Path
import json
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Pydantic Models (simplified for demo)
class Company(BaseModel):
    """Company basic information."""
    company_id: str
    legal_name: str
    brand_name: Optional[str] = None
    founded_year: Optional[int] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None
    description: str
    website: Optional[str] = None
    categories: List[str] = Field(default_factory=list)

class FundingRound(BaseModel):
    """Funding round information."""
    round_name: str  # e.g., "Series A", "Seed"
    amount_usd: Optional[float] = None
    investors: List[str] = Field(default_factory=list)
    date: Optional[str] = None
    valuation_usd: Optional[float] = None

class Leadership(BaseModel):
    """Leadership information."""
    name: str
    title: str  # CEO, CTO, etc.
    bio: Optional[str] = None

class Product(BaseModel):
    """Product information."""
    product_name: str
    description: str
    category: Optional[str] = None

class Payload(BaseModel):
    """Complete payload for one company."""
    company: Company
    funding_rounds: List[FundingRound] = Field(default_factory=list)
    leadership: List[Leadership] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    total_funding_usd: Optional[float] = None
    employee_count: Optional[int] = None
    notes: str = "Extracted from website scraping"


class StructuredExtractor:
    """Extract structured data from scraped text."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = instructor.from_openai(OpenAI(api_key=os.getenv('OPENAI_API_KEY')))
        self.model = model
        self.data_dir = Path("data/raw")
    
    def process_company(self, company_id: str) -> Optional[Payload]:
        """
        Extract structured payload for a company.
        """
        print(f"\n🔍 Extracting {company_id}...")
        
        # Load scraped data
        company_dir = self.data_dir / company_id
        if not company_dir.exists():
            print(f"  ❌ No data found")
            return None
        
        # Get latest scrape
        latest_run = sorted(company_dir.iterdir())[-1]
        
        # Load all text files
        all_text = ""
        for text_file in latest_run.glob("*.txt"):
            text = text_file.read_text(encoding='utf-8')
            all_text += f"\n\n=== {text_file.stem.upper()} ===\n{text}"
        
        if len(all_text) < 100:
            print(f"  ❌ Not enough text")
            return None
        
        # Extract structured data
        try:
            payload = self._extract_payload(all_text, company_id)
            
            if payload:
                # Save
                self._save_payload(company_id, payload)
                print(f"  ✅ Extracted successfully")
                return payload
            else:
                print(f"  ❌ Extraction failed")
                return None
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def _extract_payload(self, text: str, company_id: str) -> Optional[Payload]:
        """Use Instructor to extract structured data."""
        
        # Truncate text if too long (to save costs)
        if len(text) > 8000:
            text = text[:8000]
        
        prompt = f"""Extract structured information about this company from the provided text.

Company ID: {company_id}

Text:
{text}

Extract:
1. Company basic info (name, founded year, HQ, description, website)
2. Funding rounds (if mentioned)
3. Leadership team (CEO, CTO, founders)
4. Products/services
5. Employee count (if mentioned)
6. Total funding amount (if mentioned)

If information is not available, use None or empty list. Do not invent information."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=Payload,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction assistant. Extract only factual information from the provided text. Use 'Not disclosed' for missing data. Never invent information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_retries=2
            )
            
            return response
            
        except Exception as e:
            print(f"    Extraction error: {e}")
            return None
    
    def _save_payload(self, company_id: str, payload: Payload):
        """Save payload to JSON."""
        output_dir = Path("data/payloads")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"{company_id}.json"
        output_path.write_text(payload.model_dump_json(indent=2))


def extract_all_companies():
    """Extract structured data for all scraped companies."""
    extractor = StructuredExtractor()
    
    raw_dir = Path("data/raw")
    results = []
    
    companies = sorted([d for d in raw_dir.iterdir() if d.is_dir()])
    
    print(f"🚀 Extracting {len(companies)} companies\n")
    
    for i, company_dir in enumerate(companies, 1):
        company_id = company_dir.name
        print(f"[{i}/{len(companies)}]", end=" ")
        
        try:
            payload = extractor.process_company(company_id)
            results.append({
                'company_id': company_id,
                'success': payload is not None
            })
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append({
                'company_id': company_id,
                'success': False
            })
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 EXTRACTION COMPLETE")
    print(f"{'='*60}")
    success_count = sum(1 for r in results if r['success'])
    print(f"✅ Success: {success_count}/{len(results)}")
    
    # Save results
    Path('data/extraction_results.json').write_text(json.dumps(results, indent=2))
    print(f"\n💾 Results saved to data/extraction_results.json")
    
    return results


if __name__ == "__main__":
    extract_all_companies()