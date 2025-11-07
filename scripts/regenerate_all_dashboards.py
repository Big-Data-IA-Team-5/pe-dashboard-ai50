#!/usr/bin/env python3
"""
Regenerate all dashboards using the structured pipeline with payloads.
This ensures consistent, high-quality dashboards following the PE_Dashboard.md template.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.structured_pipeline import generate_dashboard_from_payload

def regenerate_all_dashboards():
    """Regenerate dashboards for all companies with payloads."""
    
    payloads_dir = project_root / "data" / "payloads"
    output_dir = project_root / "data" / "dashboards" / "structured"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all payload files
    payload_files = sorted(payloads_dir.glob("*.json"))
    
    if not payload_files:
        print("❌ No payload files found in data/payloads/")
        return
    
    print(f"🚀 Regenerating dashboards for {len(payload_files)} companies...")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 80)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total": len(payload_files),
        "successful": 0,
        "failed": 0,
        "companies": {}
    }
    
    for i, payload_file in enumerate(payload_files, 1):
        company_id = payload_file.stem
        print(f"\n[{i}/{len(payload_files)}] Processing: {company_id}")
        print("-" * 80)
        
        try:
            # Load payload
            with open(payload_file, 'r') as f:
                payload = json.load(f)
            
            print(f"  ✓ Loaded payload ({payload_file.stat().st_size:,} bytes)")
            
            # Generate dashboard
            result = generate_dashboard_from_payload(company_id)
            
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
                results["failed"] += 1
                results["companies"][company_id] = {
                    "status": "failed",
                    "error": result["error"]
                }
                continue
            
            # Save dashboard
            output_path = output_dir / f"{company_id}.md"
            with open(output_path, 'w') as f:
                f.write(result["dashboard"])
            
            word_count = len(result["dashboard"].split())
            print(f"  ✓ Generated dashboard ({word_count:,} words)")
            print(f"  ✓ Saved to: {output_path.name}")
            
            results["successful"] += 1
            results["companies"][company_id] = {
                "status": "success",
                "word_count": word_count,
                "output_file": str(output_path.relative_to(project_root))
            }
            
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results["failed"] += 1
            results["companies"][company_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Save results log
    log_file = project_root / "logs" / "regenerate_dashboards_results.json"
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 REGENERATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {results['successful']}/{results['total']}")
    print(f"❌ Failed: {results['failed']}/{results['total']}")
    print(f"📝 Results log: {log_file.relative_to(project_root)}")
    
    if results["successful"] > 0:
        print(f"\n✨ Successfully regenerated {results['successful']} dashboards!")
        print(f"📁 Location: {output_dir.relative_to(project_root)}/")
    
    return results

if __name__ == "__main__":
    print("🔄 Dashboard Regeneration Script")
    print("=" * 80)
    print("This script regenerates all dashboards using the structured pipeline.")
    print("Each dashboard will follow the PE_Dashboard.md template strictly.")
    print("=" * 80)
    
    try:
        results = regenerate_all_dashboards()
        sys.exit(0 if results["failed"] == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
