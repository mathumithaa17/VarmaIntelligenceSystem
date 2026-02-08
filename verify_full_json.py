
import sys
import os
import json

# Add backend/src/rag to path to match rag_service.py environment
# RAG Service adds: PROJECT_ROOT / "src" / "rag"
# From root: backend/src/rag
rag_root = os.path.join(os.getcwd(), 'backend', 'src', 'rag')
if rag_root not in sys.path:
    sys.path.insert(0, rag_root)

from src.retriever import VarmaRetriever

def test_full_json_retrieval():
    print("Initializing Retriever...")
    # Index path must be relative to CWD or absolute
    retriever = VarmaRetriever(index_path="backend/src/rag/src/varma_index.pkl")
    
    # Test a known Varma point
    varma_name = "Sevikuttri_Kaalam"
    print(f"\nTesting retrieval for: {varma_name}")
    
    full_data = retriever.get_full_json(varma_name)
    
    if full_data:
        print("SUCCESS: Retrieved Full JSON data!")
        print("Keys found:", full_data.keys())
        print("Sample Data (Indications):", full_data.get("indications"))
        
        # Verify specific fields usually missing from text chunks exist
        if "anatomicalRelations" in full_data and "tamilLiterature" in full_data:
             print("Verified: anatomicalRelations and tamilLiterature are present.")
        else:
             print("WARNING: Some expected fields are missing.")
             
        print("\nFull JSON Dump:")
        print(json.dumps(full_data, indent=2, ensure_ascii=False))
    else:
        print(f"FAILURE: Could not retrieve JSON for {varma_name}")

    # Test case insensitive
    varma_name_2 = "thilardha varmam"
    print(f"\nTesting retrieval for: {varma_name_2}")
    full_data_2 = retriever.get_full_json(varma_name_2)
    if full_data_2:
         print(f"SUCCESS: Retrieved for '{varma_name_2}' (Name in DB: {full_data_2.get('varmaName')})")
    else:
         print(f"FAILURE: Could not retrieve JSON for {varma_name_2}")

    # Test Exhaustive Search
    symptom = "headache"
    print(f"\nTesting Exhaustive Search for: {symptom}")
    matches = retriever.search_raw_json(symptom)
    print(f"Found {len(matches)} matches.")
    if len(matches) > 0:
        names = [m.get("varmaName") for m in matches]
        print(f"Match Names: {names}")
        if "Sevikuttri_Kaalam" in names:
            print("SUCCESS: Found expected point 'Sevikuttri_Kaalam'")
    else:
        print("FAILURE: Found 0 matches for 'headache'")

if __name__ == "__main__":
    test_full_json_retrieval()
