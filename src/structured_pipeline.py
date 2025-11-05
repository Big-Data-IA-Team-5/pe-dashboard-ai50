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

## Additional Context
**Notes**: {payload_dict['notes']}

**Provenance Policy**: {payload_dict['provenance_policy']}

---

## INSTRUCTIONS FOR DASHBOARD GENERATION

Generate a complete PE investor dashboard following the 8-section format.

**Critical Rules**:
1. Use ONLY the data provided in the structured payload above
2. For any missing information, write "Not disclosed."
3. NEVER invent metrics, valuations, revenue, ARR, MRR, or customer names
4. If a claim sounds like marketing, attribute it: "The company states..."
5. Include all 8 required sections in order
6. End with "## Disclosure Gaps" listing all missing critical information

**Required Sections**:
1. ## Company Overview
2. ## Business Model and GTM
3. ## Funding & Investor Profile
4. ## Growth Momentum
5. ## Visibility & Market Sentiment
6. ## Risks and Challenges
7. ## Outlook
8. ## Disclosure Gaps
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