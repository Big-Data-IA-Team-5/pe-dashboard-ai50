"""
Batch Dashboard Generator
Generates dashboards for all companies using both structured and RAG pipelines.
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

from src.models import Payload
from src.structured_pipeline import generate_structured_dashboard
from src.rag_pipeline import generate_rag_dashboard
from src.evaluator import auto_evaluate_dashboard


def load_all_payloads() -> List[Tuple[str, Payload]]:
    """Load all validated payloads from data/payloads/."""
    payloads_dir = Path("data/payloads")
    payloads = []
    
    for payload_file in sorted(payloads_dir.glob("*.json")):
        company_id = payload_file.stem
        try:
            payload = Payload.model_validate_json(payload_file.read_text())
            payloads.append((company_id, payload))
        except Exception as e:
            print(f"⚠️  Failed to load {company_id}: {e}")
    
    return payloads


def generate_dashboards_for_company(
    company_id: str,
    payload: Payload,
    index: int,
    total: int
) -> Dict[str, any]:
    """Generate both structured and RAG dashboards for a company."""
    
    print(f"\n[{index}/{total}] {payload.company_record.legal_name} ({company_id})")
    print("─" * 60)
    
    results = {
        'company_id': company_id,
        'company_name': payload.company_record.legal_name,
        'structured': {'success': False, 'error': None, 'score': None, 'path': None},
        'rag': {'success': False, 'error': None, 'score': None, 'path': None},
        'timestamp': datetime.now().isoformat()
    }
    
    # ==========================================
    # STRUCTURED PIPELINE
    # ==========================================
    try:
        print(f"🔧 STRUCTURED PIPELINE: {company_id}")
        print("=" * 60)
        
        result = generate_structured_dashboard(company_id)
        
        if 'error' in result:
            raise Exception(result['error'])
        
        structured_md = result['markdown']
        
        # Save dashboard
        structured_path = Path(f"data/dashboards/structured/{company_id}.md")
        structured_path.parent.mkdir(parents=True, exist_ok=True)
        structured_path.write_text(structured_md)
        
        # Score it
        score_result = auto_evaluate_dashboard(structured_md)
        
        results['structured'] = {
            'success': True,
            'error': None,
            'score': score_result.get('total_score', 0),
            'sections': score_result.get('sections_found', 0),
            'chars': len(structured_md),
            'path': str(structured_path)
        }
        
        print(f"  ✓ {len(structured_md)} chars, {score_result.get('sections_found', 0)}/8 sections")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")
        results['structured']['error'] = str(e)
    
    # ==========================================
    # RAG PIPELINE
    # ==========================================
    try:
        print(f"🔍 RAG PIPELINE: {company_id}")
        print("=" * 60)
        
        result = generate_rag_dashboard(company_id)
        
        if 'error' in result:
            raise Exception(result['error'])
        
        rag_md = result['markdown']
        
        # Save dashboard
        rag_path = Path(f"data/dashboards/rag/{company_id}.md")
        rag_path.parent.mkdir(parents=True, exist_ok=True)
        rag_path.write_text(rag_md)
        
        # Score it
        score_result = auto_evaluate_dashboard(rag_md)
        
        results['rag'] = {
            'success': True,
            'error': None,
            'score': score_result.get('total_score', 0),
            'sections': score_result.get('sections_found', 0),
            'chars': len(rag_md),
            'path': str(rag_path)
        }
        
        print(f"  ✓ {len(rag_md)} chars, {score_result.get('sections_found', 0)}/8 sections")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")
        results['rag']['error'] = str(e)
    
    return results


def main():
    """Main batch generation function."""
    
    print("🚀 BATCH DASHBOARD GENERATION")
    print("=" * 60)
    
    # Load all payloads
    payloads = load_all_payloads()
    total_companies = len(payloads)
    total_dashboards = total_companies * 2  # structured + RAG
    
    print(f"📊 Generating dashboards for {total_companies} companies")
    print(f"   Total dashboards: {total_dashboards}")
    print(f"   Estimated time: 6-8 hours")
    print(f"   Estimated cost: $18-20")
    print(f"   Started: {datetime.now().strftime('%I:%M %p')}")
    print()
    
    # Track results
    all_results = []
    successful_structured = 0
    successful_rag = 0
    failed_companies = []
    
    start_time = time.time()
    
    # Process each company
    for i, (company_id, payload) in enumerate(payloads, 1):
        try:
            result = generate_dashboards_for_company(company_id, payload, i, total_companies)
            all_results.append(result)
            
            if result['structured']['success']:
                successful_structured += 1
            if result['rag']['success']:
                successful_rag += 1
            
            if not result['structured']['success'] or not result['rag']['success']:
                failed_companies.append(company_id)
            
            # Print progress
            elapsed = time.time() - start_time
            avg_time_per_company = elapsed / i
            remaining_companies = total_companies - i
            eta_seconds = avg_time_per_company * remaining_companies
            eta_hours = eta_seconds / 3600
            
            print(f"\n📊 Progress: {i}/{total_companies} companies")
            print(f"   Successful: {successful_structured} structured, {successful_rag} RAG")
            print(f"   Failed: {len(failed_companies)} companies")
            print(f"   Elapsed: {elapsed/60:.1f} min")
            print(f"   ETA: {eta_hours:.1f} hours")
            print()
            
            # Save progress after each company
            progress_file = Path("logs/batch_progress.json")
            progress_file.parent.mkdir(parents=True, exist_ok=True)
            progress_file.write_text(json.dumps({
                'total_companies': total_companies,
                'processed': i,
                'successful_structured': successful_structured,
                'successful_rag': successful_rag,
                'failed_companies': failed_companies,
                'results': all_results,
                'started_at': datetime.fromtimestamp(start_time).isoformat(),
                'last_updated': datetime.now().isoformat()
            }, indent=2))
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR processing {company_id}: {e}")
            failed_companies.append(company_id)
            continue
    
    # ==========================================
    # FINAL SUMMARY
    # ==========================================
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("✅ BATCH GENERATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Results:")
    print(f"   Companies processed: {total_companies}")
    print(f"   Structured dashboards: {successful_structured}/{total_companies} ({successful_structured/total_companies*100:.1f}%)")
    print(f"   RAG dashboards: {successful_rag}/{total_companies} ({successful_rag/total_companies*100:.1f}%)")
    print(f"   Total successful: {successful_structured + successful_rag}/{total_dashboards}")
    print(f"   Failed companies: {len(failed_companies)}")
    print(f"\n⏱️  Time:")
    print(f"   Total: {total_time/3600:.2f} hours")
    print(f"   Avg per company: {total_time/total_companies:.1f} seconds")
    print(f"\n💾 Output:")
    print(f"   Structured: data/dashboards/structured/")
    print(f"   RAG: data/dashboards/rag/")
    print(f"   Progress log: logs/batch_progress.json")
    
    if failed_companies:
        print(f"\n⚠️  Failed companies ({len(failed_companies)}):")
        for company_id in failed_companies:
            print(f"     - {company_id}")
    
    print("\n" + "=" * 60)
    
    # Save final results
    final_results_file = Path("logs/batch_results_final.json")
    final_results_file.write_text(json.dumps({
        'total_companies': total_companies,
        'successful_structured': successful_structured,
        'successful_rag': successful_rag,
        'failed_companies': failed_companies,
        'total_time_hours': total_time / 3600,
        'avg_time_per_company_seconds': total_time / total_companies,
        'completed_at': datetime.now().isoformat(),
        'results': all_results
    }, indent=2))
    
    print(f"📊 Final results saved to: {final_results_file}")


if __name__ == "__main__":
    main()
