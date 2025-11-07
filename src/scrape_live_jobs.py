"""Scrape actual job listings from company career pages."""
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import time

def scrape_careers_page(company_id, website):
    """Scrape jobs from company careers page."""
    print(f"💼 {company_id}...", end=" ")
    
    # Try multiple careers URL patterns
    base = website.rstrip('/')
    careers_urls = [
        f"{base}/careers",
        f"{base}/jobs", 
        f"{base}/about/careers",
        f"{base}/company/careers",
        f"{base}/careers/jobs",
        f"{base}/join",
        f"{base}/work-with-us"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in careers_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Remove scripts/styles
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                
                text = soup.get_text(separator='\n', strip=True)
                
                if len(text) > 500:
                    # Save raw careers HTML and text
                    careers_dir = Path(f"data/careers_pages/{company_id}")
                    careers_dir.mkdir(parents=True, exist_ok=True)
                    
                    (careers_dir / "page.txt").write_text(text, encoding='utf-8')
                    (careers_dir / "page.html").write_text(resp.text, encoding='utf-8')
                    (careers_dir / "meta.json").write_text(
                        json.dumps({'url': url, 'found': True}, indent=2)
                    )
                    
                    # Count job indicators
                    job_count = text.lower().count('apply') + text.lower().count('position')
                    
                    print(f"✅ Found page ({len(text)} chars, ~{job_count} indicators)")
                    return True
        except:
            continue
    
    print("❌ No careers page")
    return False

# Load companies
companies = json.loads(Path('data/forbes_ai50_seed.json').read_text())

print(f"🚀 Scraping live careers pages for {len(companies)} companies\n")

results = []
for company in companies:
    success = scrape_careers_page(company['company_id'], company['website'])
    results.append({'company_id': company['company_id'], 'found': success})
    time.sleep(2)  # Be polite

found_count = sum(1 for r in results if r['found'])
print(f"\n✅ Found careers pages: {found_count}/{len(companies)}")