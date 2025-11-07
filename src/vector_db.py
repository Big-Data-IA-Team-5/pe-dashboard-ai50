"""Vector database for RAG pipeline using ChromaDB."""
import chromadb
from pathlib import Path
from typing import List, Dict
import json

class VectorDatabase:
    """ChromaDB wrapper for company text indexing."""
    
    def __init__(self, persist_dir: str = "data/vector_db"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="company_docs",
            metadata={"description": "Forbes AI 50 company documents"}
        )
    
    def index_company(self, company_id: str) -> int:
        """
        Index all text for a company.
        
        Returns:
            Number of chunks indexed
        """
        print(f"📚 Indexing {company_id}...", end=" ")
        
        # Load scraped data (prioritize Selenium pages)
        selenium_dir = Path("data/careers_selenium") / company_id
        raw_dir = Path("data/raw") / company_id
        
        chunks = []
        metadatas = []
        ids = []
        chunk_id = 0
        
        # First try Selenium careers page (most current)
        if selenium_dir.exists():
            page_file = selenium_dir / "page.txt"
            if page_file.exists():
                text = page_file.read_text(encoding='utf-8')
                if len(text) > 100:
                    # Chunk the text
                    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
                    
                    current_chunk = []
                    current_length = 0
                    
                    for para in paragraphs:
                        para_words = len(para.split())
                        
                        if current_length + para_words > 500:
                            # Save chunk
                            if current_chunk:
                                chunk_text = '\n\n'.join(current_chunk)
                                chunks.append(chunk_text)
                                metadatas.append({
                                    'company_id': company_id,
                                    'page_type': 'careers_selenium',
                                    'source': 'live_careers_page'
                                })
                                ids.append(f"{company_id}_selenium_{chunk_id}")
                                chunk_id += 1
                            
                            current_chunk = [para]
                            current_length = para_words
                        else:
                            current_chunk.append(para)
                            current_length += para_words
                    
                    # Save last chunk
                    if current_chunk:
                        chunk_text = '\n\n'.join(current_chunk)
                        chunks.append(chunk_text)
                        metadatas.append({
                            'company_id': company_id,
                            'page_type': 'careers_selenium',
                            'source': 'live_careers_page'
                        })
                        ids.append(f"{company_id}_selenium_{chunk_id}")
                        chunk_id += 1
        
        # Then add raw scraped pages
        if raw_dir.exists():
            latest_run = sorted(raw_dir.iterdir())[-1] if list(raw_dir.iterdir()) else None
            
            if latest_run:
                for text_file in latest_run.glob("*.txt"):
                    page_type = text_file.stem
                    text = text_file.read_text(encoding='utf-8')
                    
                    if len(text) < 100:
                        continue
                    
                    # Chunk the text
                    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
                    
                    current_chunk = []
                    current_length = 0
                    
                    for para in paragraphs:
                        para_words = len(para.split())
                        
                        if current_length + para_words > 500:
                            if current_chunk:
                                chunk_text = '\n\n'.join(current_chunk)
                                chunks.append(chunk_text)
                                metadatas.append({
                                    'company_id': company_id,
                                    'page_type': page_type,
                                    'source': 'website'
                                })
                                ids.append(f"{company_id}_{page_type}_{chunk_id}")
                                chunk_id += 1
                            
                            current_chunk = [para]
                            current_length = para_words
                        else:
                            current_chunk.append(para)
                            current_length += para_words
                    
                    if current_chunk:
                        chunk_text = '\n\n'.join(current_chunk)
                        chunks.append(chunk_text)
                        metadatas.append({
                            'company_id': company_id,
                            'page_type': page_type,
                            'source': 'website'
                        })
                        ids.append(f"{company_id}_{page_type}_{chunk_id}")
                        chunk_id += 1
        
        # Add to ChromaDB
        if chunks:
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ {len(chunks)} chunks")
        else:
            print(f"⚠️ No chunks")
        
        return len(chunks)
    
    def search(self, company_id: str, query: str, k: int = 5) -> List[Dict]:
        """
        Search for relevant chunks.
        
        Args:
            company_id: Filter by company
            query: Search query
            k: Number of results
            
        Returns:
            List of dicts with 'text', 'metadata', 'score'
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where={"company_id": company_id}
        )
        
        if not results['documents'][0]:
            return []
        
        return [
            {
                'text': doc,
                'metadata': meta,
                'score': 1.0 - dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': self.collection.name
        }


def index_all_companies():
    """Index all companies."""
    print("🚀 Building Vector Database for RAG\n")
    
    vdb = VectorDatabase()
    
    # Get all companies
    raw_dir = Path("data/raw")
    companies = sorted([d.name for d in raw_dir.iterdir() if d.is_dir()])
    
    results = []
    
    for i, company_id in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] ", end="")
        
        try:
            num_chunks = vdb.index_company(company_id)
            results.append({
                'company_id': company_id,
                'chunks': num_chunks
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'company_id': company_id,
                'chunks': 0
            })
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 VECTOR DB COMPLETE")
    print(f"{'='*60}")
    
    total_chunks = sum(r['chunks'] for r in results)
    companies_indexed = sum(1 for r in results if r['chunks'] > 0)
    
    print(f"✅ Total chunks: {total_chunks:,}")
    print(f"🏢 Companies indexed: {companies_indexed}/{len(companies)}")
    print(f"📁 Database: data/vector_db/")
    
    # Save stats
    stats = vdb.get_stats()
    print(f"\n💾 ChromaDB stats: {stats}")
    
    return results


if __name__ == "__main__":
    index_all_companies()
    
    # Test search
    print("\n🧪 Testing search...")
    vdb = VectorDatabase()
    results = vdb.search("anthropic", "funding investors", k=3)
    print(f"✅ Search test: Found {len(results)} results")
    if results:
        print(f"   Sample: {results[0]['text'][:100]}...")