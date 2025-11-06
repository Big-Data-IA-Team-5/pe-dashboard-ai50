"""Adapter to convert P1's payload format to Pydantic Payload format."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import date
from src.models import (
    Payload, Company, Event, Product, Leadership,
    Snapshot, Visibility
)


def adapt_p1_payload(p1_data: Dict[str, Any], company_id: str) -> Payload:
    """
    Convert P1's payload structure to match Pydantic Payload model.
    
    P1's format:
    - company, products, executives, funding_rounds, recent_news
    
    Our format (models.py):
    - company_record, events, products, leadership, snapshots, visibility
    
    Args:
        p1_data: P1's JSON structure
        company_id: Company identifier
        
    Returns:
        Validated Payload object
    """
    # ==========================================
    # MAP: company → company_record
    # ==========================================
    p1_company = p1_data.get('company', {})
    
    # Handle website - must be valid URL or None
    website = p1_company.get('website')
    if website and ('not disclosed' in website.lower() or not website.startswith('http')):
        website = None
    
    company = Company(
        company_id=p1_company.get('company_id', company_id),
        legal_name=p1_company.get('legal_name', p1_company.get('company_name', company_id.title())),
        brand_name=p1_company.get('brand_name', p1_company.get('legal_name')),
        website=website,
        hq_city=p1_company.get('hq_city'),
        hq_state=p1_company.get('hq_state'),
        hq_country=p1_company.get('hq_country'),
        founded_year=p1_company.get('founded_year'),
        categories=[p1_company.get('category', 'AI')] if p1_company.get('category') else ['AI'],
        as_of=date.today() if p1_company.get('as_of') is None else p1_company.get('as_of')
    )
    
    # ==========================================
    # MAP: funding_rounds → events (type=funding)
    # ==========================================
    events = []
    for i, fr in enumerate(p1_data.get('funding_rounds', []), 1):
        # Parse date if string
        occurred_date = fr.get('date', fr.get('announced_date'))
        if isinstance(occurred_date, str):
            try:
                occurred_date = date.fromisoformat(occurred_date)
            except:
                occurred_date = date.today()
        elif occurred_date is None:
            occurred_date = date.today()
            
        event = Event(
            event_id=f"{company_id}_funding_{i}",
            company_id=company_id,
            event_type='funding',
            occurred_on=occurred_date,
            title=f"{fr.get('round_type', 'Funding Round')}",
            description=f"{fr.get('round_type', 'Funding')}: {fr.get('amount', fr.get('amount_usd', 'Not disclosed.'))}",
            investors=fr.get('lead_investors', fr.get('investors', [])),
            amount_usd=fr.get('amount_usd')
        )
        events.append(event)
    
    # Add recent_news as events too
    for i, news in enumerate(p1_data.get('recent_news', []), 1):
        # Parse date if string
        occurred_date = news.get('date')
        if isinstance(occurred_date, str):
            try:
                occurred_date = date.fromisoformat(occurred_date)
            except:
                occurred_date = date.today()
        elif occurred_date is None:
            occurred_date = date.today()
            
        event = Event(
            event_id=f"{company_id}_news_{i}",
            company_id=company_id,
            event_type='other',  # 'news' is not in the Literal list
            occurred_on=occurred_date,
            title=news.get('title', news.get('headline', 'News item')),
            description=news.get('title', news.get('headline', 'News item'))
        )
        events.append(event)
    
    # ==========================================
    # MAP: products (adjust schema)
    # ==========================================
    products = []
    for i, prod in enumerate(p1_data.get('products', []), 1):
        product = Product(
            product_id=f"{company_id}_product_{i}",
            company_id=company_id,
            name=prod.get('product_name', prod.get('name', f'Product {i}')),
            description=prod.get('description'),
            pricing_model=prod.get('pricing_model')
        )
        products.append(product)
    
    # ==========================================
    # MAP: executives/founders → leadership
    # ==========================================
    leadership = []
    
    # Add executives
    for i, exec in enumerate(p1_data.get('executives', []), 1):
        lead = Leadership(
            person_id=f"{company_id}_exec_{i}",
            company_id=company_id,
            name=exec.get('name', 'Not disclosed.'),
            role=exec.get('title', exec.get('role', 'Executive')),
            linkedin=exec.get('linkedin_url')
        )
        leadership.append(lead)
    
    # Add founders
    for i, founder in enumerate(p1_data.get('founders', []), 1):
        lead = Leadership(
            person_id=f"{company_id}_founder_{i}",
            company_id=company_id,
            name=founder.get('name', 'Not disclosed.'),
            role='Founder',
            is_founder=True
        )
        leadership.append(lead)
    
    # ==========================================
    # CREATE: snapshots (from metrics if available)
    # ==========================================
    snapshots = []
    metrics = p1_data.get('metrics', {})
    if metrics:
        snapshot = Snapshot(
            company_id=company_id,
            as_of=date.today(),
            headcount_total=metrics.get('employee_count'),
            engineering_openings=metrics.get('engineering_openings'),
            sales_openings=metrics.get('sales_openings')
        )
        snapshots.append(snapshot)
    
    # ==========================================
    # CREATE: visibility (empty for now)
    # ==========================================
    visibility = []
    
    # ==========================================
    # ASSEMBLE: Final Payload
    # ==========================================
    payload = Payload(
        company_record=company,
        events=events,
        snapshots=snapshots,
        products=products,
        leadership=leadership,
        visibility=visibility,
        notes=p1_data.get('notes', 'Extracted from P1 pipeline, adapted to Pydantic schema.'),
        provenance_policy="Only use explicitly stated information. Use 'Not disclosed.' for missing data."
    )
    
    return payload


def convert_all_payloads():
    """Convert all P1 payloads to correct Pydantic schema."""
    source_dir = Path("data/payloads_complete")
    target_dir = Path("data/payloads")
    target_dir.mkdir(exist_ok=True)
    
    print("🔄 CONVERTING P1's PAYLOADS TO PYDANTIC SCHEMA")
    print("=" * 60)
    
    payload_files = list(source_dir.glob("*.json"))
    print(f"Found {len(payload_files)} payloads to convert\n")
    
    success = 0
    failed = 0
    errors = []
    
    for payload_file in payload_files:
        company_id = payload_file.stem
        
        try:
            # Load P1's data (handle encoding issues)
            with open(payload_file, 'r', encoding='utf-8', errors='replace') as f:
                p1_data = json.load(f)
            
            # Convert to Pydantic format
            payload = adapt_p1_payload(p1_data, company_id)
            
            # Validate it works
            payload.model_validate(payload.model_dump())
            
            # Save in correct format
            output_path = target_dir / f"{company_id}.json"
            output_path.write_text(payload.model_dump_json(indent=2))
            
            print(f"  ✓ {company_id:20} → {len(payload.events)} events, {len(payload.products)} products, {len(payload.leadership)} leadership")
            success += 1
            
        except Exception as e:
            print(f"  ✗ {company_id:20} → Error: {str(e)[:50]}")
            failed += 1
            errors.append({'company_id': company_id, 'error': str(e)})
    
    print("\n" + "=" * 60)
    print(f"✅ CONVERSION COMPLETE!")
    print(f"   Success: {success}/{len(payload_files)} ({success/len(payload_files)*100:.1f}%)")
    print(f"   Failed: {failed}/{len(payload_files)}")
    
    if failed > 0:
        print(f"\n⚠️  Failed companies:")
        for err in errors:
            print(f"     - {err['company_id']}: {err['error'][:60]}")
    
    print(f"\n💾 Converted payloads saved to: data/payloads/")
    print("=" * 60)
    
    return success, failed


if __name__ == "__main__":
    success, failed = convert_all_payloads()
    
    if success >= 45:
        print(f"\n🎉 SUCCESS! {success} payloads ready for batch generation!")
    else:
        print(f"\n⚠️  Only {success} payloads converted. Check errors above.")
