#!/usr/bin/env python3
"""
Build ChromaDB Vector Database for RAG Pipeline

This script processes all scraped company data and builds a ChromaDB
vector database for semantic search in the RAG pipeline.

Usage:
    python scripts/build_vector_db.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_db import build_vector_db_for_all_companies


if __name__ == "__main__":
    print("🏗️  Building Vector Database for RAG Pipeline")
    print("=" * 70)
    print()
    
    # Build the database
    vdb = build_vector_db_for_all_companies()
    
    print("\n" + "=" * 70)
    print("✅ Vector database build complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Test RAG search: python -m src.vector_db")
    print("2. Generate RAG dashboard: Use Streamlit UI or API")
    print("3. The database is persisted in: data/chroma_db/")
    print()
