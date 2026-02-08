from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import re
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
            # Depth-based JSON finder (robust against conversational noise)
            start_idx = router_response_raw.find('{')
            if start_idx != -1:
                depth = 0
                for i in range(start_idx, len(router_response_raw)):
                    if router_response_raw[i] == '{': depth += 1
                    elif router_response_raw[i] == '}': depth -= 1
                    if depth == 0:
                        json_str = router_response_raw[start_idx : i + 1]
                        router_result = json.loads(json_str)
                        break
            
            if not router_result or "intent" not in router_result:
                raise ValueError("No valid JSON intent found")

        except Exception as e:
            print(f"Router parsing failed: {e}")
            # Identify intent from keywords as last resort
            lower_q = question.lower()
            if any(k in lower_q for k in ["vs", "difference", "compare", "distinguish"]):
                intent = "VARMA_POINT"
                # Fallback extraction: Look for capitalized names or quoted strings
                extracted = re.findall(r"['\"](.*?)['\"]", question)
                if not extracted:
                    # Simple heuristic: capitalized words (excluding first word of sentence)
                    words = question.split()
                    extracted = [w.strip("?,.!") for i, w in enumerate(words) if i > 0 and w[0].isupper()]
                search_term = extracted
            else:
                intent = "SYMPTOM"
                search_term = question.split()[-1].strip("?,.!") # Guess last word
            router_result = {"intent": intent, "search_term": search_term}

        intent = router_result.get("intent") or "SYMPTOM"
        search_term = router_result.get("search_term")

        # --- REFINEMENT: Aggressively handle malformed lists or messy strings ---
        if isinstance(search_term, (str, list)):
            str_term = str(search_term)
            # Find everything inside quotes
            extracted = re.findall(r"['\"](.*?)['\"]", str_term)
            if not extracted:
                # If no quotes and it looks list-like, split by comma
                if '[' in str_term or ',' in str_term:
                    extracted = [s.strip("[]'\" ") for s in re.split(r'[,;]', str_term) if s.strip()]
            
            if extracted:
                # Filter out garbage
                search_term = [s for s in extracted if len(s) > 2]
            elif isinstance(search_term, str):
                # Just a single string
                search_term = [search_term]
            elif not search_term:
                search_term = []

        print(f"Router Decision: Intent={intent}, Term='{search_term}'")
        sys.stdout.flush()



        
        # ------------------------------------------------------------------
        # STEP 2: RETRIEVAL (STRICT)
        # ------------------------------------------------------------------
        context = ""
        sources = []
        results = [] # Initialize results here to ensure it's always defined

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
                # Format search_term for display
                if isinstance(search_term, list):
                    display_term = " and ".join([f"'{t}'" for t in search_term])
                else:
                    display_term = f"'{search_term}'"
                
                # STRICT MODE: Do not generate if no data found.
                return jsonify({
                    "answer": f"I apologize, but I could not find any specific Varma points relating to {display_term} in the traditional database.",
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

