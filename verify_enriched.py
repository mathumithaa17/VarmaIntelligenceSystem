
import requests
import json
import time

BASE_URL = "http://localhost:5004/api/rag/query"

def test_enriched():
    print("Testing Enriched Retrieval (Single Turn)...")
    
    question = "Which Varma points are used for headaches?"
    payload = {
        "question": question,
        "history": []
    }
    
    print(f"\nQuestion: {question}")
    try:
        resp = requests.post(BASE_URL, json=payload)
        data = resp.json()
        ans = data.get("answer", "")
        print(f"Answer Length: {len(ans)}")
        print(f"Answer Snippet: {ans[:300]}...")
        
        # Check for detailed content
        # We expect descriptions of Sevikuttri, Visha_Manibantha, Utchi, etc.
        # Simple check: does it mention "Location" or "Indications" which are part of full docs?
        
        needed_terms = ["Location", "Indications", "Sevikuttri", "Visha_Manibantha"]
        found = [t for t in needed_terms if t in ans]
        
        print(f"\nFound terms: {found}")
        
        if len(found) >= 3:
             print("\n[SUCCESS] Answer appears to contain enriched details.")
        else:
             print("\n[WARNING] Answer might lack full details. Check 'rag_service.py' logs for enrichment.")

    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_enriched()
