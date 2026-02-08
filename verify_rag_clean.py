
import sys
import os
from pathlib import Path

print("DEBUG: Start of clean script")
current_file = Path(__file__).resolve()
rag_root = current_file.parent / "backend" / "src" / "rag"
sys.path.insert(0, str(rag_root))

try:
    from src.retriever import VarmaRetriever
    from src.llm.prompt import build_prompt
    from src.llm.generator import generate
    print("Imports successful")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_query(retriever, query, description, file_handle):
    file_handle.write(f"\n--- TEST: {description} ---\n")
    file_handle.write(f"Query: {query}\n")
    
    docs = retriever.retrieve(query, top_k=5)
    context = "\n\n".join([d["text"] for d in docs])
    
    if not context:
        file_handle.write("Context: [EMPTY]\n")
    else:
        file_handle.write(f"Context Snippet: {context[:200]}...\n")

    prompt = build_prompt(query, context)
    response = generate(prompt)
    file_handle.write(f"Response:\n{response}\n")
    return response

def main():
    print(f"Script started. Root: {rag_root}")
    index_path = rag_root / "varma_index.pkl"
    
    if not index_path.exists():
        print(f"Index not found at {index_path}")
        return

    print("Initializing retriever...")
    retriever = VarmaRetriever(index_path=str(index_path))
    print("Retriever initialized.")

    output_file = "verification_report.txt"
    print(f"Writing to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        # Test 1: In-domain question
        test_query(retriever, "What are the indications for Thilardha Varmam?", "In-Domain / Specific Varma", f)

        # Test 2: Tamil Literature
        test_query(retriever, "What is the tamil literature for Thilardha Varmam?", "Tamil Literature Extraction", f)

        # Test 3: Out-of-domain
        test_query(retriever, "Who won the cricket world cup in 2011?", "Out-of-Domain", f)

        # Test 4: Another Out-of-domain (medical but not Varma)
        test_query(retriever, "How do I treat a common cold with antibiotics?", "Out-of-Domain (Medical)", f)

    print("Verification complete. Results written to verification_report.txt")

if __name__ == "__main__":
    main()
