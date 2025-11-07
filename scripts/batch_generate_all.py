#!/usr/bin/env python3
"""
BATCH DASHBOARD GENERATION - DIRECT PYTHON
Generates dashboards for all 50 Forbes AI 50 companies using:
- Structured pipeline: For 48 companies with converted Pydantic payloads
- RAG pipeline: For all 50 companies using GCS ChromaDB

No API calls - direct Python imports.
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')
from src.structured_pipeline import generate_structured_dashboard
from src.rag_pipeline import generate_rag_dashboard

print("🚀 BATCH DASHBOARD GENERATION (DIRECT PYTHON)")
print("=" * 80)

# Load all companies from seed
seed = json.load(open("data/forbes_ai50_seed.json"))
all_companies = [c['company_id'] for c in seed]

# Check which have payloads
payloads_available = set(f.stem for f in Path("data/payloads").glob("*.json"))

print(f"Total companies: {len(all_companies)}")
print(f"With Pydantic payloads: {len(payloads_available)}")
print(f"Started: {datetime.now().strftime('%I:%M %p')}\n")

# Results tracking
structured_success = 0
rag_success = 0
structured_failed = []
rag_failed = []
results = []

start_time = time.time()

for i, company_id in enumerate(all_companies, 1):
    print(f"[{i}/50] {company_id:30}", end=" ", flush=True)
    
    company_result = {
        'company_id': company_id,
        'structured': {'success': False, 'error': None},
        'rag': {'success': False, 'error': None}
    }
    
    # ==========================================
    # STRUCTURED PIPELINE (if payload exists)
    # ==========================================
    if company_id in payloads_available:
        try:
            result = generate_structured_dashboard(company_id)
            
            if 'error' not in result:
                output = Path(f"data/dashboards/structured/{company_id}.md")
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(result['markdown'])
                
                structured_success += 1
                company_result['structured']['success'] = True
                company_result['structured']['chars'] = len(result['markdown'])
                print("✅ S", end=" ", flush=True)
            else:
                structured_failed.append(company_id)
                company_result['structured']['error'] = result['error']
                print("❌ S", end=" ", flush=True)
                
        except Exception as e:
            structured_failed.append(company_id)
            company_result['structured']['error'] = str(e)
            print(f"❌ S", end=" ", flush=True)
    else:
        print("⊘ S", end=" ", flush=True)  # No payload available
    
    # ==========================================
    # RAG PIPELINE (all companies)
    # ==========================================
    try:
        result = generate_rag_dashboard(company_id, use_gcs=True, top_k=50)  # Get ALL chunks
        
        if 'error' not in result:
            output = Path(f"data/dashboards/rag/{company_id}.md")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(result['markdown'])
            
            rag_success += 1
            company_result['rag']['success'] = True
            company_result['rag']['chars'] = len(result['markdown'])
            print("✅ R", flush=True)
        else:
            rag_failed.append(company_id)
            company_result['rag']['error'] = result['error']
            print("❌ R", flush=True)
            
    except Exception as e:
        rag_failed.append(company_id)
        company_result['rag']['error'] = str(e)
        print(f"❌ R", flush=True)
    
    results.append(company_result)

# ==========================================
# FINAL SUMMARY
# ==========================================
total_time = time.time() - start_time

print(f"\n{'=' * 80}")
print(f"✅ BATCH GENERATION COMPLETE!")
print(f"{'=' * 80}")
print(f"📊 Results:")
print(f"   Structured: {structured_success}/{len(payloads_available)} ({structured_success/len(payloads_available)*100:.1f}%)")
print(f"   RAG: {rag_success}/50 ({rag_success/50*100:.1f}%)")
print(f"   Total dashboards: {structured_success + rag_success}")

print(f"\n⏱️  Time:")
print(f"   Total: {total_time/60:.1f} minutes")
print(f"   Avg per company: {total_time/50:.1f} seconds")

print(f"\n📁 Output:")
print(f"   data/dashboards/structured/ - {structured_success} files")
print(f"   data/dashboards/rag/ - {rag_success} files")

if structured_failed:
    print(f"\n⚠️  Structured failed ({len(structured_failed)}): {', '.join(structured_failed)}")
if rag_failed:
    print(f"⚠️  RAG failed ({len(rag_failed)}): {', '.join(rag_failed)}")

# Save results
results_file = Path("logs/batch_generation_results.json")
results_file.parent.mkdir(parents=True, exist_ok=True)
results_file.write_text(json.dumps({
    'total_companies': len(all_companies),
    'structured_success': structured_success,
    'rag_success': rag_success,
    'structured_failed': structured_failed,
    'rag_failed': rag_failed,
    'total_time_seconds': total_time,
    'completed_at': datetime.now().isoformat(),
    'results': results
}, indent=2))

print(f"\n💾 Results saved: {results_file}")
print(f"{'=' * 80}")
