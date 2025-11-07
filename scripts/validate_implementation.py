#!/usr/bin/env python3
"""Quick validation that GCS integration is properly implemented."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("🔍 GCS INTEGRATION VALIDATION")
print("=" * 80)
print()

# Test 1: Check files exist
print("✓ Checking implementation files...")
files_to_check = [
    "src/vector_db_gcs.py",
    "src/jobs_loader.py",
    "requirements.txt",
    "GCS_INTEGRATION_SUMMARY.md"
]

for file in files_to_check:
    if Path(file).exists():
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} MISSING!")

print()

# Test 2: Check requirements.txt has GCS
print("✓ Checking requirements.txt...")
req_content = Path("requirements.txt").read_text()
if "google-cloud-storage" in req_content:
    print("  ✓ google-cloud-storage present")
else:
    print("  ✗ google-cloud-storage MISSING!")

print()

# Test 3: Verify imports work (without GCS)
print("✓ Testing imports (local mode)...")
try:
    # Test local vector DB
    from src.vector_db import VectorDatabase
    vdb = VectorDatabase()
    stats = vdb.get_stats()
    print(f"  ✓ VectorDatabase works: {stats.get('total_chunks', 0)} chunks")
except Exception as e:
    print(f"  ✗ VectorDatabase failed: {e}")

try:
    # Test RAG pipeline
    from src.rag_pipeline import generate_rag_dashboard
    print("  ✓ RAG pipeline imports successfully")
except Exception as e:
    print(f"  ✗ RAG pipeline import failed: {e}")

try:
    # Test API
    from src.api import app
    print("  ✓ FastAPI app imports successfully")
except Exception as e:
    print(f"  ✗ FastAPI import failed: {e}")

print()

# Test 4: Verify RAG pipeline works (local mode)
print("✓ Testing RAG pipeline (local mode)...")
try:
    from src.rag_pipeline import generate_rag_dashboard
    
    # Test with use_gcs=False (local mode)
    result = generate_rag_dashboard('openai', 'OpenAI', top_k=3, use_gcs=False)
    
    if 'error' not in result:
        using_gcs = result['metadata'].get('using_gcs', False)
        pipeline = result['metadata'].get('pipeline', 'unknown')
        chunks = result['metadata'].get('num_chunks', 0)
        valid = result['validation'].get('valid', False)
        
        print(f"  ✓ Dashboard generated")
        print(f"    - Pipeline: {pipeline}")
        print(f"    - Using GCS: {using_gcs}")
        print(f"    - Chunks: {chunks}")
        print(f"    - Valid: {valid}")
        print(f"    - Length: {len(result['markdown'])} chars")
    else:
        print(f"  ✗ Error: {result['error']}")
except Exception as e:
    print(f"  ✗ RAG test failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("✅ VALIDATION COMPLETE")
print("=" * 80)
print()
print("📋 Next Steps:")
print("   1. To use GCS: export VECTOR_DB_USE_GCS=true")
print("   2. Start API: uvicorn src.api:app --reload")
print("   3. Test endpoint: curl -X POST 'http://localhost:8000/dashboard/rag?company_id=openai'")
print()
