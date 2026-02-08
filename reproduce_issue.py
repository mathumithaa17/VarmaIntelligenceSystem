
import sys
import os
from pathlib import Path

# Add backend/src/rag to sys.path
current_file = Path(__file__).resolve()
rag_root = current_file.parent / "backend" / "src" / "rag"
sys.path.insert(0, str(rag_root))

from src.retriever import VarmaRetriever

def reproduce():
    print("Initializing retriever...")
    index_path = rag_root / "varma_index.pkl"
    if not index_path.exists():
        print("Index not found.")
        return
    
    retriever = VarmaRetriever(index_path=str(index_path))
    
    # Turn 1: Headache
    query1 = "Which Varma points are used for headaches?"
    print(f"\nTurn 1 Query: {query1}")
    docs1 = retriever.retrieve(query1, top_k=5)
    print("Turn 1 Docs:")
    for d in docs1:
        print(f" - {d.get('text', '')[:50]}...")
        
    # Turn 2: Follow-up
    query2 = "explain each varma points"
    print(f"\nTurn 2 Query: {query2}")
    docs2 = retriever.retrieve(query2, top_k=5)
    print("Turn 2 Docs (Expected: Detailed Varma descriptions, Actual: Likely irrelevant):")
    for d in docs2:
        print(f" - {d.get('text', '')[:100]}...")
        
    # Check if 'Sevikuttri' or 'Thilardha' or similar appear in Turn 2 docs
    found_details = any("Sevikuttri" in d.get("text", "") for d in docs2)
    if not found_details:
        print("\n[FAILURE] Turn 2 did not retrieve details for Varma points mentioned in Turn 1.")
    else:
        print("\n[SUCCESS] Turn 2 retrieved relevant details.")

if __name__ == "__main__":
    reproduce()
