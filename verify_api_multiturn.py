
import requests
import json
import time

BASE_URL = "http://localhost:5004/api/rag/query"

def test_multiturn():
    print("Testing Multi-Turn RAG API...")
    
    # Turn 1
    question1 = "Which Varma points are used for headaches?"
    payload1 = {
        "question": question1,
        "history": []
    }
    
    print(f"\nTurn 1: {question1}")
    try:
        resp1 = requests.post(BASE_URL, json=payload1)
        data1 = resp1.json()
        ans1 = data1.get("answer", "")
        print(f"Answer 1: {ans1[:100]}...")
    except Exception as e:
        print(f"Turn 1 Failed: {e}")
        return

    # Turn 2
    question2 = "explain each varma points"
    history = [
        {"role": "user", "content": question1},
        {"role": "assistant", "content": ans1}
    ]
    payload2 = {
        "question": question2,
        "history": history
    }
    
    print(f"\nTurn 2: {question2}")
    try:
        resp2 = requests.post(BASE_URL, json=payload2)
        data2 = resp2.json()
        ans2 = data2.get("answer", "")
        print(f"Answer 2: {ans2[:200]}...")
        
        # Verification
        if "Sevikuttri" in ans2 or "Thilardha" in ans2 or "Visha" in ans2 or "Utchi" in ans2:
            print("\n[SUCCESS] Turn 2 response contains details of Varma points.")
        else:
             # It might mention "Sevikuttri" in the text even if not in the first few chars
             if len(ans2) > 200 and ("Sevikuttri" in ans2 or "Visha" in ans2):
                 print("\n[SUCCESS] Turn 2 response contains details.")
             else:
                print("\n[FAILURE] Turn 2 response does not seem to contain detailed Varma info.")
                print(f"Full Answer 2: {ans2}")

    except Exception as e:
        print(f"Turn 2 Failed: {e}")

if __name__ == "__main__":
    test_multiturn()
