import requests
import json
import sys

BASE_URL = "http://localhost:5004/api/rag/query"

def test_query(query, description):
    print(f"\n--- Testing: {description} ---")
    print(f"Query: '{query}'")
    try:
        response = requests.post(BASE_URL, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            print(f"Status: {response.status_code}")
            print(f"Answer Preview: {answer[:300]}...")
            if "I am designed to answer questions only about Varma points" in answer:
                 print("[RESULT]: REJECTED (Expected for out-of-context)")
            else:
                 print("[RESULT]: RESPONDED")
            
            # Check for sources if expected
            return data
        else:
            print(f"Error: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    # 1. Symptom Test
    test_query("headache", "Symptom Lookup")

    # 2. Varma Point Test
    test_query("Utchi Varmam", "Varma Point Name Lookup")
    
    # 3. Fuzzy Symptom Test
    test_query("I have a severe head ache", "Fuzzy Symptom Lookup (Old)")
    test_query("I have a headache", "Natural Language 'headache'")
    test_query("head ache", "Spaced 'head ache'")

    # 4. Out of Context Test
    test_query("What is the capital of France?", "Out of Context")
    
    # 5. Out of Context Test 2
    test_query("tell me a joke", "Out of Context 2")
