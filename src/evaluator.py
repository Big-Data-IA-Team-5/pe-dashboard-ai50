"""Enhanced evaluation logic for dashboard comparison."""
from typing import Dict, List
import re


def score_dashboard(
    factual: int,
    schema: int,
    provenance: int,
    hallucination: int,
    readability: int
) -> int:
    """
    Calculate total rubric score.
    
    Args:
        factual: 0-3 points
        schema: 0-2 points
        provenance: 0-2 points
        hallucination: 0-2 points
        readability: 0-1 points
        
    Returns:
        Total score (0-10)
    """
    return factual + schema + provenance + hallucination + readability


def auto_evaluate_dashboard(markdown: str) -> Dict[str, int]:
    """
    Automated evaluation of dashboard quality.
    
    Note: Factual correctness requires human verification.
    This provides automated scoring for other criteria.
    
    Args:
        markdown: Generated dashboard markdown
        
    Returns:
        Dictionary of scores for each criterion
    """
    scores = {
        "factual": 2,  # Default, requires manual verification
        "schema": 0,
        "provenance": 0,
        "hallucination": 0,
        "readability": 0
    }
    
    # Schema adherence (0-2): Check for all 8 required sections
    required_sections = [
        "## Company Overview",
        "## Business Model and GTM",
        "## Funding & Investor Profile",
        "## Growth Momentum",
        "## Visibility & Market Sentiment",
        "## Risks and Challenges",
        "## Outlook",
        "## Disclosure Gaps"
    ]
    
    present_count = sum(1 for section in required_sections if section in markdown)
    
    if present_count == 8:
        scores["schema"] = 2
    elif present_count >= 6:
        scores["schema"] = 1
    else:
        scores["schema"] = 0
    
    # Provenance (0-2): Check for "Not disclosed" usage
    not_disclosed_count = markdown.lower().count("not disclosed")
    
    if not_disclosed_count >= 3:
        scores["provenance"] = 2
    elif not_disclosed_count >= 1:
        scores["provenance"] = 1
    else:
        scores["provenance"] = 0
    
    # Hallucination control (0-2): Check for warning phrases
    hallucination_phrases = [
        "we believe", "it appears", "likely", "probably",
        "estimated to be", "rumored", "sources say", "reportedly",
        "it seems", "may have", "could be", "presumably",
        "it is believed", "allegedly"
    ]
    
    hallucination_count = sum(
        1 for phrase in hallucination_phrases 
        if phrase in markdown.lower()
    )
    
    if hallucination_count == 0:
        scores["hallucination"] = 2
    elif hallucination_count <= 2:
        scores["hallucination"] = 1
    else:
        scores["hallucination"] = 0
    
    # Readability (0-1): Check length and formatting
    word_count = len(markdown.split())
    has_structure = "## " in markdown
    has_lists = ("- " in markdown or "* " in markdown)
    
    if 500 <= word_count <= 3000 and has_structure:
        scores["readability"] = 1
    else:
        scores["readability"] = 0
    
    return scores


def compare_dashboards(
    rag_markdown: str,
    structured_markdown: str,
    company_name: str
) -> Dict:
    """
    Compare RAG vs Structured dashboards using rubric.
    
    Args:
        rag_markdown: Dashboard from RAG pipeline
        structured_markdown: Dashboard from Structured pipeline
        company_name: Company name for reporting
        
    Returns:
        Comparison results with scores and winner
    """
    # Evaluate both
    rag_scores = auto_evaluate_dashboard(rag_markdown)
    struct_scores = auto_evaluate_dashboard(structured_markdown)
    
    # Calculate totals
    rag_total = sum(rag_scores.values())
    struct_total = sum(struct_scores.values())
    
    return {
        "company_name": company_name,
        "rag": {
            **rag_scores,
            "total": rag_total
        },
        "structured": {
            **struct_scores,
            "total": struct_total
        },
        "winner": "structured" if struct_total > rag_total else "rag",
        "difference": abs(struct_total - rag_total),
        "rag_strengths": _identify_strengths(rag_scores),
        "structured_strengths": _identify_strengths(struct_scores)
    }


def _identify_strengths(scores: Dict[str, int]) -> List[str]:
    """Identify which criteria a pipeline performed well on."""
    strengths = []
    
    if scores.get("factual", 0) >= 2:
        strengths.append("factual accuracy")
    if scores.get("schema", 0) == 2:
        strengths.append("schema adherence")
    if scores.get("provenance", 0) >= 1:
        strengths.append("provenance tracking")
    if scores.get("hallucination", 0) == 2:
        strengths.append("hallucination control")
    if scores.get("readability", 0) == 1:
        strengths.append("readability")
    
    return strengths


if __name__ == "__main__":
    # Test evaluator
    test_markdown = """
## Company Overview
TestAI is a company. Not disclosed.

## Business Model and GTM
Not disclosed.

## Funding & Investor Profile
Not disclosed.

## Growth Momentum
Not disclosed.

## Visibility & Market Sentiment
Not disclosed.

## Risks and Challenges
Not disclosed.

## Outlook
Not disclosed.

## Disclosure Gaps
- Revenue not disclosed
- Customer names not disclosed
"""
    
    scores = auto_evaluate_dashboard(test_markdown)
    print("Test Scores:", scores)
    print("Total:", sum(scores.values()), "/10")