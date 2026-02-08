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
from src.retriever import RuleBasedRetriever
from src.llm.prompt import build_prompt
from src.llm.generator import generate
from src.llm.router_prompt import ROUTER_PROMPT_TEMPLATE

# Check for FAISS (Optional, largely unused now but kept for legacy compat if needed)
try:
    import faiss
except ImportError:
    pass 


app = Flask(__name__)
CORS(app)

# ==============================================================================
# INITIALIZATION
# ==============================================================================
print("\n" + "="*80)
print("INITIALIZING RAG SERVICE (PORT 5004)")
print("="*80)

retriever = None
# Initialize Retriever (Loads JSONs into memory)
print("Initializing Rule-Based Retriever...")
try:
    retriever = RuleBasedRetriever()
except Exception as e:
    print(f"Failed to initialize retriever: {e}")
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
    data = request.json
    question = data.get("query") or data.get("question", "")
    history = data.get("history", [])
    
    # 1. Construct chat history string
    history_text = ""
    for h in history[-5:]: # Increased history context
        role = h.get("role", "user")
        content = h.get("content", "")
        history_text += f"{role.upper()}: {content}\n"

    print(f"\n--- Processing Query: '{question}' ---")
    print(f"Request Payload: {data}")
    sys.stdout.flush()


    try:
        # ------------------------------------------------------------------
        # STEP 1: ROUTER & EXTRACTION (LLM DECISION)
        # ------------------------------------------------------------------
        router_prompt = ROUTER_PROMPT_TEMPLATE.format(
            history=history_text, 
            query=question
        )
        
        print("Invoking Router Step...")
        sys.stdout.flush()

        router_response_raw = generate(router_prompt)




        
        # Parse JSON output from LLM
        import json
        router_result = {}
        try:
            # Robust JSON extraction: Find first '{' and last '}'
            start_idx = router_response_raw.find('{')
            end_idx = router_response_raw.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = router_response_raw[start_idx : end_idx + 1]
                router_result = json.loads(json_str)
            else:
                raise ValueError("No JSON object found in response")

        except Exception as e:
            print(f"Router parsing failed: {e}. Raw: {router_response_raw}")
            # Fallback: Assume symptom if simple failure, or just fail safe
            router_result = {"intent": "SYMPTOM", "search_term": question}

        intent = router_result.get("intent") or "SYMPTOM" # Default to SYMPTOM if None or missing
        search_term = router_result.get("search_term")
        
        print(f"Router Decision: Intent={intent}, Term='{search_term}'")
        sys.stdout.flush()



        
        # ------------------------------------------------------------------
        # STEP 2: RETRIEVAL (STRICT)
        # ------------------------------------------------------------------
        context = ""
        sources = []
        
        if intent == "OUT_OF_CONTEXT":
            # Early rejection
            return jsonify({
                "answer": "I am designed to answer questions only about Varma points and their related symptoms based on the traditional medical data. Please ask about a specific Varma point or symptom.",
                "sources": [],
                "confidence": 1.0, # High confidence that we shouldn't answer
                "debug_intent": intent,
                "debug_term": search_term,
                "debug_query_received": question
            }), 200

            
        elif intent in ["SYMPTOM", "VARMA_POINT"] and search_term:
            # Handle List of Terms (Comparisons)
            results = []
            if isinstance(search_term, list):
                print(f"Comparison Query: Fetching data for {len(search_term)} terms: {search_term}")
                for term in search_term:
                    # Fetch and verify each term
                    term_results = retriever.fetch_data(str(term), intent)
                    if term_results:
                        results.extend(term_results)
            else:
                # Single Term
                results = retriever.fetch_data(str(search_term), intent)

            print(f"Retrieved {len(results)} total records")
            
            if not results:
                # STRICT MODE: Do not generate if no data found.
                return jsonify({
                    "answer": f"I apologize, but I could not find any specific Varma points relating to '{search_term}' in the traditional database.",
                    "sources": [],
                    "confidence": 0.0,
                    "debug_intent": intent,
                    "debug_term": search_term,
                    "debug_query_received": question
                }), 200
            else:
                context_parts = []
                for item in results:
                    json_str = json.dumps(item, indent=2, ensure_ascii=False)
                    header = f"VARMA POINT: {item.get('varmaName', 'Unknown')}"
                    context_parts.append(f"[{header}]\n{json_str}")
                    sources.append(item.get('varmaName', 'Unknown'))
                context = "\n\n".join(context_parts)

        else:
            context = "System: Could not determine clear search intent."

        # ------------------------------------------------------------------
        # STEP 3: GENERATION (LLM SYNTHESIS)
        # ------------------------------------------------------------------
        # Update prompt to include the specific intent and strict context
        prompt = build_prompt(question, context, history_text)
        
        print("Generating answer with LLM...")
        response_text = generate(prompt)
        print("LLM Response received.")

        response = {
            "answer": response_text,
            "sources": list(set(sources)),
            "confidence": 1.0 if sources else 0.5,
            "debug_intent": intent,
            "debug_term": search_term
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTING VARMA RULE-BASED SERVICE")
    print("="*80)
    # Disable debug/reloader to ensure logs are captured in redirection
    app.run(debug=False, port=5004, host='0.0.0.0')

