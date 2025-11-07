#!/usr/bin/env python3
"""Generate RAG dashboards for all 50 companies using ChromaDB."""
import requests
import time
from pathlib import Path
from datetime import datetime

API_BASE = "http://localhost:8000"

# Get all companies from seed file
import json
seed = json.load(open("data/forbes_ai50_seed.json"))
companies = [c['company_id'] for c in seed]

print(f"🚀 RAG DASHBOARD GENERATION (GCS ChromaDB)")
print(f"=" * 80)
print(f"Companies: {len(companies)}")
print(f"Data Source: gs://us-central1-pe-airflow-env-2825d831-bucket/data/vector_db/")
print(f"Started: {datetime.now().strftime('%I:%M %p')}\n")

success = 0
failed = []

for i, cid in enumerate(companies, 1):
    print(f"[{i}/{len(companies)}] {cid:30}", end=" → ", flush=True)
    
    try:
        resp = requests.post(
            f"{API_BASE}/dashboard/rag", 
            params={"company_id": cid, "use_gcs": True, "top_k": 8},
            timeout=90
        )
        
        if resp.status_code == 200:
            data = resp.json()
            Path(f"data/dashboards/rag/{cid}.md").write_text(data['markdown'])
            success += 1
            sections = data['validation']['section_count']
            chars = len(data['markdown'])
            print(f"✅ {chars} chars, {sections}/8 sections", flush=True)
        else:
            print(f"❌ HTTP {resp.status_code}", flush=True)
            failed.append(cid)
    except Exception as e:
        print(f"❌ {str(e)[:40]}", flush=True)
        failed.append(cid)
    
    time.sleep(1)  # Rate limiting for API

print(f"\n{'=' * 80}")
print(f"✅ COMPLETE!")
print(f"Success: {success}/{len(companies)} ({success/len(companies)*100:.1f}%)")
if failed:
    print(f"Failed ({len(failed)}): {', '.join(failed[:10])}")
print(f"={'=' * 80}")
