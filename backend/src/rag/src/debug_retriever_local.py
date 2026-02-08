import sys
from pathlib import Path

# Adjust path to find the module
base_path = Path(__file__).resolve().parent # backend/src/rag/src
sys.path.append(str(base_path))

from retriever import RuleBasedRetriever

def debug_lookup(retriever, query):
    print(f"\nQUERY: '{query}'")
    match_type, results = retriever.lookup(query)
    print(f"Match Type: {match_type}")
    print(f"Result Count: {len(results)}")
    if results:
        print(f"First Result: {results[0].get('varmaName')}")
    else:
        print("NO MATCH")

if __name__ == "__main__":
    print("Initializing Retriever...")
    r = RuleBasedRetriever()
    
    # Test cases
    queries = [
        "headache",
        "I have a headache",
        "head ache",
        "I have a head ache",
        "severe headache",
        "my head hurts"
    ]
    
    for q in queries:
        debug_lookup(r, q)
