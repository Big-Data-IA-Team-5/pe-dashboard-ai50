"""Web scraper for AI company websites."""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import json
import time
from typing import Dict, Optional

class CompanyScraper:
    """Scraper for AI company homepages and about pages."""
    
    def __init__(self, storage_dir: str = "data/raw"):
        self.storage = Path(storage_dir)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36'
        }
    
    def scrape_company(self, company_id: str, website: str) -> Dict:
        """
        Scrape multiple pages for a company.
        
        Args:
            company_id: Unique identifier (e.g., 'openai')
            website: Company website URL
            
        Returns:
            Dict with page data
        """
        results = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_dir = self.storage / company_id / timestamp
        company_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n🔍 Scraping {company_id}...")
        
        # Clean website URL (remove /?list=ai50 if present)
        website = website.split('?')[0]
        base_url = website.rstrip('/')
        
        # Pages to scrape
        pages = {
            'homepage': base_url,
            'about': f"{base_url}/about",
            'about-us': f"{base_url}/about-us",
            'company': f"{base_url}/company",
            'careers': f"{base_url}/careers",
            'blog': f"{base_url}/blog"
        }
        
        for page_name, url in pages.items():
            page_data = self._scrape_page(url, page_name)
            if page_data and len(page_data.get('text', '')) > 200:
                self._save_page(company_dir, page_name, page_data)
                results[page_name] = page_data
                print(f"    ✓ {page_name}")
            else:
                print(f"    ✗ {page_name} (not found or too short)")
            
            time.sleep(1)  # Be polite, wait between requests
        
        # Save summary
        summary = {
            'company_id': company_id,
            'website': website,
            'scraped_at': datetime.now().isoformat(),
            'pages_found': list(results.keys()),
            'total_pages': len(results)
        }
        (company_dir / 'summary.json').write_text(json.dumps(summary, indent=2))
        
        return results
    
    def _scrape_page(self, url: str, page_type: str) -> Optional[Dict]:
        """Scrape a single page and return clean text."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove noise
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe', 'noscript']):
                tag.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)
            
            return {
                'text': clean_text,
                'url': url,
                'status': 'success',
                'scraped_at': datetime.now().isoformat(),
                'char_count': len(clean_text)
            }
            
        except requests.Timeout:
            return None
        except Exception as e:
            return None
    
    def _save_page(self, company_dir: Path, page_type: str, data: Dict):
        """Save scraped page to disk."""
        # Save text
        (company_dir / f"{page_type}.txt").write_text(data['text'], encoding='utf-8')
        
        # Save metadata
        metadata = {
            'url': data['url'],
            'scraped_at': data['scraped_at'],
            'status': data['status'],
            'char_count': data['char_count']
        }
        (company_dir / f"{page_type}_meta.json").write_text(
            json.dumps(metadata, indent=2)
        )


def scrape_all_companies():
    """Scrape all companies from seed file."""
    # Load companies
    seed_path = Path('data/forbes_ai50_seed.json')
    if not seed_path.exists():
        print("❌ forbes_ai50_seed.json not found!")
        return
    
    with open(seed_path) as f:
        companies = json.load(f)
    
    print(f"🚀 Starting scraper for {len(companies)} companies\n")
    
    scraper = CompanyScraper()
    results = []
    
    for i, company in enumerate(companies, 1):
        print(f"\n[{i}/{len(companies)}]", end=" ")
        
        try:
            result = scraper.scrape_company(
                company['company_id'],
                company['website']
            )
            
            results.append({
                'company_id': company['company_id'],
                'company_name': company.get('company_name', ''),
                'success': len(result) > 0,
                'pages_scraped': len(result)
            })
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append({
                'company_id': company['company_id'],
                'success': False,
                'error': str(e)
            })
        
        # Small delay between companies
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 SCRAPING COMPLETE")
    print(f"{'='*50}")
    success_count = sum(1 for r in results if r['success'])
    print(f"✅ Success: {success_count}/{len(results)}")
    
    total_pages = sum(r.get('pages_scraped', 0) for r in results)
    print(f"📄 Total pages: {total_pages}")
    
    # Save results
    Path('data/scraping_results.json').write_text(json.dumps(results, indent=2))
    print(f"\n💾 Results saved to data/scraping_results.json")
    
    return results


if __name__ == "__main__":
    scrape_all_companies()