import sys
from pathlib import Path
import json

# Add src to path
# We need to point to backend/src/rag effectively
base_path = Path(__file__).resolve().parent # backend
rag_path = base_path / "src" / "rag"
sys.path.insert(0, str(rag_path))

from src.llm.generator import generate
from src.llm.router_prompt import ROUTER_PROMPT_TEMPLATE

def test_router(query, history=""):
    print(f"\n--- Testing Query: '{query}' ---")
    prompt = ROUTER_PROMPT_TEMPLATE.format(history=history, query=query)
    
    print("Generating...")
    start_time = time.time()
    response = generate(prompt)
    elapsed = time.time() - start_time
    print(f"Raw Response ({elapsed:.2f}s):\n{response}")
    
    try:
        clean_json = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        print("Parsed JSON:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"JSON Parsing Failed: {e}")

import time

if __name__ == "__main__":
    test_router("my head hurts")
    test_router("tell me about utchi varmam")
    test_router("who is the president?")
