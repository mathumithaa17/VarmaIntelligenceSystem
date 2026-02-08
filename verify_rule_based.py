
import sys
import os
import json

# Add backend path
rag_root = os.path.join(os.getcwd(), 'backend', 'src', 'rag')
if rag_root not in sys.path:
    sys.path.insert(0, rag_root)

from src.retriever import RuleBasedRetriever

def test_rule_based():
    print("Initializing RuleBasedRetriever...")
    retriever = RuleBasedRetriever()
    
    tests = [
        ("headache", "symptom", ["Sevikuttri_Kaalam", "Visha_Manibantha_Varmam", "Utchi_Varmam"]),
        ("Utchi Varmam", "varma", ["Utchi_Varmam"]),
        ("Football", None, []),
        ("severe headache", "symptom", ["Sevikuttri_Kaalam"]), # Substring check
        ("thilardha", "varma", ["Thilardha_Varmam"]) # Substring name check
    ]
    
    for query, expected_type, expected_items in tests:
        print(f"\nQuery: '{query}'")
        m_type, results = retriever.lookup(query)
        
        # Check Type
        if m_type == expected_type:
            print(f"  ✓ Type Match: {m_type}")
        else:
            print(f"  ✗ Type Mismatch: Expected {expected_type}, Got {m_type}")
            
        # Check Content
        if expected_items is None or len(expected_items) == 0:
            if not results:
                 print("  ✓ Correctly returned no results.")
            else:
                 print(f"  ✗ Expected no results, got {len(results)}")
        else:
            if not results:
                print(f"  ✗ Expected results {expected_items}, got None")
                continue
                
            found_names = [r.get("varmaName", "") for r in results]
            print(f"  Found: {found_names}")
            
            # Check if at least one expected item is found
            missing = [e for e in expected_items if e not in found_names]
            if len(missing) == 0:
                 print("  ✓ All expected items found.")
            elif len(missing) < len(expected_items):
                 print(f"  ~ Partial match. Missing: {missing}")
            else:
                 print(f"  ✗ No expected items found. Expected overlap with {expected_items}")

if __name__ == "__main__":
    test_rule_based()
