
import sys
from pathlib import Path

# Setup path
import os
current_dir = Path(__file__).resolve().parent
rag_root = current_dir / "backend" / "src" / "rag"
sys.path.insert(0, str(rag_root))

from src.retriever import VarmaRetriever

def debug():
    print("Loading Retriever...")
    retriever = VarmaRetriever(str(rag_root / "varma_index.pkl"))
    
    query = "headaches"
    print(f"\nQuery: {query}")
    
    docs = retriever.retrieve(query, top_k=15)
    
    print(f"\nFound {len(docs)} documents:\n")
    for i, doc in enumerate(docs):
        doc_id = doc.get('id', 'Unknown')
        snippet = doc.get('text', '')[:100].replace('\n', ' ')
        print(f"{i+1}. [{doc_id}] {snippet}...")
        
        # Check if target is here
        if "Aanantha_vayu_Kalam" in doc_id:
            print("   >>> FOUND TARGET!")

if __name__ == "__main__":
    debug()
