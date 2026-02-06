from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path

# ==============================================================================
# CONFIGURATION & PATHS
# ==============================================================================
# We need to add 'backend/src/rag' to sys.path so that 'import src.retriever'
# (which expects to be inside backend/src/rag) works correctly and resolves
# its own internal 'from src...' imports.
PROJECT_ROOT = Path(__file__).resolve().parent
RAG_ROOT = PROJECT_ROOT / "src" / "rag"

if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

# Now we can import from the preferred RAG implementation
from src.retriever import VarmaRetriever
from src.llm.prompt import build_prompt
from src.llm.generator import generate

# Check for FAISS (common missing dependency on new envs)
try:
    import faiss
except ImportError:
    print("\n" + "!"*80)
    print("[CRITICAL ERROR] 'faiss' module not found.")
    print("Please run: pip install faiss-cpu")
    print("!"*80 + "\n")


app = Flask(__name__)
CORS(app)

# ==============================================================================
# INITIALIZATION
# ==============================================================================
print("\n" + "="*80)
print("INITIALIZING RAG SERVICE (PORT 5004)")
print("="*80)

retriever = None
try:
    # VarmaRetriever defaults to loading 'varma_index.pkl'.
    # We must provide the full path since we are running from backend/
    index_path = RAG_ROOT / "varma_index.pkl"
    print(f"Loading retriever index from: {index_path}")
    
    if not index_path.exists():
        print(f"✗ Error: Index file not found at {index_path}")
    else:
        retriever = VarmaRetriever(index_path=str(index_path))
        print("\n✓ RAG Retriever initialized successfully!")

except Exception as e:
    print(f"\n✗ Failed to initialize retriever: {e}")


# ==============================================================================
# API ROUTES
# ==============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Varma RAG Service (Text-based)",
        "retriever_loaded": retriever is not None
    })

@app.route('/api/rag/query', methods=['POST'])
def rag_query():
    """RAG question answering endpoint"""
    try:
        if retriever is None:
            return jsonify({"error": "Retriever not initialized"}), 500

        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({"error": "Empty question"}), 400
        
        # 1-B. Process History
        history = data.get('history', [])
        # Provide last 5 turns to keep context window manageable
        history_text = ""
        if history:
            relevant_history = history[-6:] # Last 3 exchanges
            history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in relevant_history])

        print(f"\nRAG Question: {question}")
        
        # 1. Retrieve relevant documents (returns list of dicts with 'text' key)
        docs = retriever.retrieve(question, top_k=20) # Increased to 20 per user request
        
        # 2. Build Context
        context = "\n\n--- DOCUMENT SEPARATOR ---\n\n".join([d.get("text", "") for d in docs])
        
        # 3. Build Prompt
        prompt = build_prompt(question, context, history_text)
        
        print("Generating answer with LLM...")
        
        # 4. Generate Answer
        # Note: generate() in this version might handle 'model' internally or default
        response_text = generate(prompt)
        
        print("LLM Response received.")

        # 5. Format response
        # The frontend expects a JSON with 'answer', 'sources', 'confidence'
        # Since the simpler retriever doesn't return structured source metadata or confidence scores
        # in the same way, we provide simplified values.
        
        response = {
            "answer": response_text,
            "sources": ["Varma Text Index"], # Simplified source
            "confidence": 1.0 # Placeholder confidence
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"✗ RAG Query Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTING VARMA RAG SERVICE")
    print("="*80)
    print(f"Service running at: http://localhost:5004")
    print("="*80 + "\n")
    
    app.run(debug=True, port=5004, host='0.0.0.0')
