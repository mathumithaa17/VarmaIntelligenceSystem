import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent
RAG_ROOT = PROJECT_ROOT / "src" / "rag"

print(f"RAG_ROOT: {RAG_ROOT}")
sys.path.insert(0, str(RAG_ROOT))

print(f"sys.path[0]: {sys.path[0]}")
print(f"sys.path[1]: {sys.path[1]}")

try:
    import src
    print(f"src file: {src.__file__}")
    
    from src.llm.router_prompt import ROUTER_PROMPT_TEMPLATE
    print("Imported ROUTER_PROMPT_TEMPLATE successfully!")
    
    from src.retriever import RuleBasedRetriever
    print("Imported RuleBasedRetriever successfully!")
    
except Exception as e:
    print(f"Failed: {e}")
