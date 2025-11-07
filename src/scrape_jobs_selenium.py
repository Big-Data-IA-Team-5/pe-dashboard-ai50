"""Scrape live job listings using Selenium."""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from pathlib import Path
import time

def scrape_jobs_with_selenium(company_id, website):
    """Scrape jobs using Selenium to handle JavaScript."""
    print(f"\n🌐 {company_id}...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run without opening browser
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Try multiple careers URLs
    base = website.rstrip('/')
    careers_urls = [
        f"{base}/careers",
        f"{base}/jobs",
        f"{base}/careers/jobs",
        f"{base}/company/careers"
    ]
    
    for url in careers_urls:
        try:
            print(f"  Trying: {url}")
            
            # Initialize driver
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Load page
            driver.get(url)
            
            # Wait for page to load (up to 10 seconds)
            time.sleep(5)  # Give JavaScript time to load
            
            # Get page source after JavaScript execution
            page_source = driver.page_source
            driver.quit()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove scripts/styles
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            if len(text) > 1000:
                # Save
                careers_dir = Path(f"data/careers_selenium/{company_id}")
                careers_dir.mkdir(parents=True, exist_ok=True)
                
                (careers_dir / "page.txt").write_text(text, encoding='utf-8')
                (careers_dir / "page.html").write_text(page_source, encoding='utf-8')
                (careers_dir / "meta.json").write_text(
                    json.dumps({'url': url, 'chars': len(text)}, indent=2)
                )
                
                # Count job-related keywords
                job_indicators = (
                    text.lower().count('engineer') +
                    text.lower().count('manager') +
                    text.lower().count('director') +
                    text.lower().count('specialist') +
                    text.lower().count('analyst')
                )
                
                print(f"  ✅ Saved ({len(text)} chars, ~{job_indicators} job keywords)")
                return True
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            try:
                driver.quit()
            except:
                pass
            continue
    
    print(f"  ❌ No careers page found")
    return False

# Load companies
companies = json.loads(Path('data/forbes_ai50_seed.json').read_text())

print(f"🚀 Selenium scraping for {len(companies)} companies")
print(f"⏱️  This will take 10-15 minutes (loading JavaScript)\n")

results = []
for i, company in enumerate(companies, 1):
    print(f"[{i}/{len(companies)}]", end=" ")
    success = scrape_jobs_with_selenium(company['company_id'], company['website'])
    results.append({'company_id': company['company_id'], 'found': success})

found = sum(1 for r in results if r['found'])
print(f"\n✅ Scraped careers pages with Selenium: {found}/{len(companies)}")
print(f"📁 Saved to: data/careers_selenium/")