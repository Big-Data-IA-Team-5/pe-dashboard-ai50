"""Structured pipeline: Pydantic payload → LLM → PE Dashboard."""
from pathlib import Path
from typing import Optional
import json

from src.models import Payload
from src.llm_client import get_llm_client


# Data directory
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "payloads"


def load_payload(company_id: str) -> Optional[Payload]:
    """
    Load and validate Pydantic payload from file.
    
    Args:
        company_id: Company identifier (e.g., 'openai')
        
    Returns:
        Validated Payload object or None if not found
    """
    payload_path = DATA_DIR / f"{company_id}.json"
    
    # Try company-specific payload
    if not payload_path.exists():
        # Fallback to starter payload for testing
        starter_path = Path(__file__).resolve().parents[1] / "data" / "starter_payload.json"
        if starter_path.exists():
            print(f"⚠️  No payload for {company_id}, using starter payload for testing")
            payload_path = starter_path
        else:
            print(f"❌ No payload found for {company_id}")
            return None
    
    try:
        # Load and validate with Pydantic
        payload_json = payload_path.read_text()
        payload = Payload.model_validate_json(payload_json)
        return payload
    except Exception as e:
        print(f"❌ Failed to load/validate payload: {e}")
        return None


def generate_structured_dashboard(company_id: str) -> dict:
    """
    Generate PE dashboard using structured Pydantic payload.
    
    This is Lab 8: Structured Pipeline Dashboard.
    Pipeline: Validated Payload → Formatted JSON → LLM → Markdown Dashboard
    
    Args:
        company_id: Company identifier
        
    Returns:
        {
            "markdown": str,           # Generated dashboard
            "payload": dict,           # Original payload data
            "validation": dict,        # Structure validation results
            "metadata": dict           # Generation metadata
        }
    """
    print(f"\n🔧 STRUCTURED PIPELINE: {company_id}")
    print("=" * 60)
    
    # Step 1: Load payload
    payload = load_payload(company_id)
    if not payload:
        return {
            "error": "Payload not found",
            "markdown": f"## Error\n\nNo structured payload found for company: {company_id}\n\nPlease ensure P1 has completed extraction for this company.",
            "payload": None,
            "validation": {"valid": False, "error": "No payload"}
        }
    
    print(f"✓ Loaded payload")
    print(f"  Company: {payload.company_record.legal_name}")
    print(f"  Events: {len(payload.events)}")
    print(f"  Products: {len(payload.products)}")
    print(f"  Leadership: {len(payload.leadership)}")
    print(f"  Snapshots: {len(payload.snapshots)}")
    
    # Step 2: Convert payload to dict and format for LLM
    payload_dict = payload.model_dump(mode='json')
    
    # Step 2.5: Load comprehensive jobs data from GCS
    jobs_section = ""
    jobs_detail = []
    try:
        from src.jobs_loader import get_jobs_loader
        jobs_loader = get_jobs_loader()
        
        # Get full job listings, not just summary
        jobs = jobs_loader.get_jobs_for_company(company_id)
        job_summary = jobs_loader.get_job_summary(company_id)
        
        if job_summary.get('available', False) and len(jobs) > 0:
            jobs_section = f"""
## Jobs/Hiring Data (Current Open Positions)
**Total Positions**: {job_summary['total_jobs']}
- **Engineering roles**: {job_summary['engineering_jobs']}
- **Sales/Business roles**: {job_summary['sales_jobs']}
- **Other roles**: {job_summary['other_jobs']}

**Job Listings** (Top positions):
"""
            # Add detailed job information
            for i, job in enumerate(jobs[:15], 1):  # Include up to 15 jobs
                title = job.get('title', 'Unknown')
                location = job.get('location', 'Not specified')
                dept = job.get('department', 'Not specified')
                
                jobs_section += f"{i}. **{title}** - {location}"
                if dept != 'Not specified':
                    jobs_section += f" ({dept})"
                jobs_section += "\n"
                
                # Store detailed info for context
                jobs_detail.append({
                    'title': title,
                    'location': location,
                    'department': dept
                })
            
            if len(jobs) > 15:
                jobs_section += f"\n... and {len(jobs) - 15} more positions\n"
            
            print(f"✓ Jobs data loaded: {job_summary['total_jobs']} positions with full details")
        else:
            print(f"  No jobs data available")
            jobs_section = "\n## Jobs/Hiring Data\nNo job listings data available.\n"
    except Exception as e:
        print(f"  Jobs data error: {e}")
        jobs_section = "\n## Jobs/Hiring Data\nCould not load job listings.\n"
    
    # Step 3: Create context for LLM
    context = f"""# Structured Data Payload for PE Dashboard Generation

## Company Information
```json
{json.dumps(payload_dict['company_record'], indent=2)}
```

## Funding & Events ({len(payload_dict['events'])} events)
```json
{json.dumps(payload_dict['events'], indent=2)}
```

## Products ({len(payload_dict['products'])} products)
```json
{json.dumps(payload_dict['products'], indent=2)}
```

## Leadership ({len(payload_dict['leadership'])} entries)
```json
{json.dumps(payload_dict['leadership'], indent=2)}
```

## Snapshots ({len(payload_dict['snapshots'])} snapshots)
```json
{json.dumps(payload_dict['snapshots'], indent=2)}
```

## Visibility Metrics ({len(payload_dict['visibility'])} entries)
```json
{json.dumps(payload_dict['visibility'], indent=2)}
```
{jobs_section}
## Additional Context
**Notes**: {payload_dict['notes']}

**Provenance Policy**: {payload_dict['provenance_policy']}

---

## INSTRUCTIONS FOR COMPREHENSIVE DASHBOARD GENERATION

Generate a DETAILED, COMPREHENSIVE PE investor dashboard using ALL data provided above.

**Data Sources Available**:
- ✅ Company record (legal info, HQ, categories, funding totals)
- ✅ Events array (funding rounds, partnerships, product launches, leadership changes)
- ✅ Products array (complete product catalog with descriptions and pricing)
- ✅ Leadership array (executive team with names, titles, founder status)
- ✅ Snapshots array (headcount, growth rates, job openings over time)
- ✅ Visibility metrics (news mentions, sentiment, GitHub stars, Glassdoor ratings)
- ✅ Jobs/Hiring data (current open positions by category and department)

**Critical Rules**:
1. **USE EVERY PIECE OF DATA** - Don't skip any arrays or fields
2. **BE SPECIFIC** - Use actual numbers, names, dates, and amounts from the data
3. **LIST EVERYTHING**:
   - List ALL executive names and titles from Leadership array
   - List ALL products with descriptions from Products array  
   - List ALL funding rounds with dates, amounts, investors from Events array
   - List ALL job categories and counts from Jobs data
   - Include EXACT metrics from Snapshots (headcount numbers, growth %, job openings)
   - Include EXACT numbers from Visibility (news mentions count, sentiment score)
4. **For missing data only**: Write "Not disclosed."
5. **Never invent** metrics, valuations, revenue, ARR, MRR, or customer names
6. **If marketing claims**: Attribute them: "The company states..."
7. **Be comprehensive**: Dashboards should be 1500-3000 words, not brief summaries

**Required Sections (with comprehensive content)**:

1. ## Company Overview
   - Legal name, brand name, HQ location, founded year
   - ALL categories from company record
   - **Leadership Team**: List EVERY executive with name, title, founder status
   - Related/competitor companies

2. ## Business Model and GTM
   - Target customers, pricing model
   - **ALL Products**: Describe EACH product by name with features and pricing
   - Integration partners (list all by name)
   - Reference customers (list all by name)
   - Specific pricing tiers if available

3. ## Funding & Investor Profile
   - **COMPLETE Funding History**: List EVERY funding event chronologically
     - For each round: Date (YYYY-MM-DD), Round name, Amount ($XXM format), Investors (all names), Valuation if disclosed
   - Totals from company record: total_raised_usd, last_round_name, last_valuation

4. ## Growth Momentum
   - **From Snapshots**: Most recent headcount (exact number), growth rate (%), job openings breakdown (engineering vs sales vs other)
   - **From Jobs Data**: Current hiring - total positions, by category (engineering/sales/other), sample job titles
   - **From Events**: ALL partnerships, product releases, leadership changes with dates and descriptions

5. ## Visibility & Market Sentiment
   - **EXACT metrics** from Visibility array:
     - News mentions: "[X] mentions in past 30 days"
     - Sentiment score: "[X.XX] on -1 to +1 scale"
     - GitHub stars: "[X] stars"
     - Glassdoor rating: "[X.X]/5.0"
   - Trend analysis if multiple visibility entries exist

6. ## Risks and Challenges
   - From Events: layoffs, regulatory issues, security incidents
   - From Leadership: executive turnover (end_date populated)
   - Competitive pressure from related_companies
   - Any challenges mentioned in notes

7. ## Outlook
   - Moat: data advantages, integrations, proprietary tech
   - Team strength: founder pedigree, executive backgrounds
   - GTM scaling indicators: sales vs engineering hiring ratio
   - Market position and competitive landscape
   - Product momentum from release events

8. ## Disclosure Gaps
   - Bullet list of EVERY missing critical metric:
     - Valuation (if not in events or company_record)
     - Revenue/ARR (if not disclosed)
     - Customer count (if reference_customers empty)
     - Growth metrics (if snapshots empty)
     - Leadership backgrounds (if education/previous_affiliation empty)
     - etc.

**Target length**: 1500-3000 words for comprehensive analysis
"""
    
    # Step 4: Call LLM
    print(f"\n🤖 Calling LLM (gpt-4o-mini)...")
    print(f"  Context size: {len(context)} chars")
    
    llm = get_llm_client()
    markdown = llm.generate_dashboard(context, temperature=0.2)
    
    print(f"✓ Dashboard generated: {len(markdown)} chars")
    
    # Step 5: Validate structure
    validation = llm.validate_structure(markdown)
    
    print(f"\n📊 Validation Results:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Sections: {validation['section_count']}/8")
    
    if not validation['valid']:
        print(f"  ⚠️  Missing sections: {validation['missing_sections']}")
    
    if not validation['has_disclosure_gaps']:
        print(f"  ⚠️  Missing '## Disclosure Gaps' section")
    
    # Step 6: Return complete result
    return {
        "markdown": markdown,
        "payload": payload_dict,
        "validation": validation,
        "metadata": {
            "company_id": company_id,
            "company_name": payload.company_record.legal_name,
            "pipeline": "structured",
            "model": llm.model,
            "num_events": len(payload.events),
            "num_products": len(payload.products),
            "num_leadership": len(payload.leadership),
            "num_snapshots": len(payload.snapshots),
            "context_length": len(context),
            "output_length": len(markdown)
        }
    }


def test_structured_pipeline():
    """Test structured pipeline with starter payload."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing Structured Pipeline")
    print("=" * 60)
    
    # Test with starter payload (UUID from starter file)
    company_id = "00000000-0000-0000-0000-000000000000"
    
    result = generate_structured_dashboard(company_id)
    
    if "error" not in result:
        print("\n✅ STRUCTURED PIPELINE TEST PASSED")
        print("\n" + "=" * 60)
        print("GENERATED DASHBOARD:")
        print("=" * 60)
        print(result['markdown'])
        print("=" * 60)
        
        print(f"\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
        
        print(f"\nValidation:")
        print(f"  Sections: {result['validation']['section_count']}/8")
        print(f"  Valid: {result['validation']['valid']}")
        
        return True
    else:
        print(f"\n❌ STRUCTURED PIPELINE TEST FAILED")
        print(f"Error: {result['error']}")
        return False


if __name__ == "__main__":
    test_structured_pipeline()