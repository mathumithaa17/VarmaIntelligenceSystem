import sys
import os
from pathlib import Path

print("Mini debug started")
current_file = Path(__file__).resolve()
print(f"Current file: {current_file}")
rag_root = current_file.parent / "backend" / "src" / "rag"
print(f"Computed rag_root: {rag_root}")

sys.path.insert(0, str(rag_root))
print(f"sys.path: {sys.path}")


try:
    print("Attempting import src.retriever...")
    from src.retriever import VarmaRetriever
    print("Import retriever successful")

    print("Attempting import src.llm...")
    from src.llm.prompt import build_prompt
    from src.llm.generator import generate
    print("Import llm successful")

    print("Attempting to instantiate VarmaRetriever...")
    index_path = rag_root / "varma_index.pkl"
    if index_path.exists():
        retriever = VarmaRetriever(index_path=str(index_path))
        print("Instantiation successful")
    else:
        print("Index not found, skipping instantiation")

except Exception as e:
    print(f"Crash detected: {e}")
    import traceback
    traceback.print_exc()

print("Mini debug finished")
