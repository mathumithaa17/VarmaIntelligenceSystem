
import sys
import os
from pathlib import Path
import re

# Add backend/src/rag to sys.path
current_file = Path(__file__).resolve()
rag_root = current_file.parent / "backend" / "src" / "rag"
sys.path.insert(0, str(rag_root))

from src.retriever import VarmaRetriever

def debug_enrichment():
    print("Initializing retriever...")
    index_path = rag_root / "varma_index.pkl"
    retriever = VarmaRetriever(index_path=str(index_path))
    
    query = "Which Varma points are used for headaches?"
    print(f"\nQuery: {query}")
    
    # 1. Initial Retrieval
    docs = retriever.retrieve(query, top_k=5)
    print(f"Initial Docs found: {len(docs)}")
    
    seen_ids = set(d.get("id") for d in docs if "id" in d)
    extra_docs = []
    
    # 2. Enrichment Logic
    print("\nScanning for Related Varma Points...")
    for d in docs:
        text = d.get("text", "")
        # Regex from rag_service.py
        match = re.search(r"Related Varma Points:\s*(.*)", text, re.IGNORECASE)
        if match:
            points_str = match.group(1)
            print(f"Found match: '{points_str}'")
            points = [p.strip() for p in points_str.split(",") if p.strip()]
            for p in points:
                print(f"  - Looking up: '{p}'")
                varma_doc = retriever.retrieve_by_name(p)
                if varma_doc:
                    print(f"    -> FOUND doc id: {varma_doc.get('id')}")
                    vid = varma_doc.get("id")
                    if vid and vid not in seen_ids:
                        extra_docs.append(varma_doc)
                        seen_ids.add(vid)
                else:
                    print(f"    -> NOT FOUND")
        else:
            # print("  - No match in this doc")
            pass

    print(f"\nEnrichment Result: Added {len(extra_docs)} extra docs.")
    
    # Check content of extra docs
    for d in extra_docs:
        print(f"\n--- Extra Doc ({d.get('id')}) ---")
        print(d.get("text", "")[:200])

if __name__ == "__main__":
    debug_enrichment()
