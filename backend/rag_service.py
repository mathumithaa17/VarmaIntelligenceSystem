"""
Clean RAG Service - Simplified Flow
Router → Fetch → Generate
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import re
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
RAG_ROOT = PROJECT_ROOT / "src" / "rag"

if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

# Import RAG components
from src.retriever import RuleBasedRetriever
from src.llm.generator import generate
from src.llm.router_prompt import ROUTER_PROMPT_TEMPLATE
from src.llm.prompt import GENERATOR_PROMPT_TEMPLATE

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize retriever
print("=" * 80)
print("INITIALIZING RAG SERVICE (PORT 5004)")
print("=" * 80)
print("Initializing Rule-Based Retriever...")
retriever = RuleBasedRetriever()
print("\n" + "=" * 80)
print("STARTING VARMA RULE-BASED SERVICE")
print("=" * 80)

def format_history_for_llm(history):
    """Format chat history for LLM context."""
    if not history:
        return "No previous conversation."
    
    formatted = []
    for msg in history[-5:]:  # Last 5 messages for context
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        formatted.append(f"{role.upper()}: {content}")
    
    return "\n".join(formatted)

def extract_json_from_response(response: str) -> dict:
    """Extract JSON object from LLM response."""
    # Find first { and matching }
    start = response.find('{')
    if start == -1:
        return {}
    
    depth = 0
    for i in range(start, len(response)):
        if response[i] == '{':
            depth += 1
        elif response[i] == '}':
            depth -= 1
            if depth == 0:
                json_str = response[start:i+1]
                try:
                    return json.loads(json_str)
                except:
                    return {}
    return {}

@app.route('/api/rag/query', methods=['POST', 'OPTIONS'])
def rag_query():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        question = data.get('question', '')
        # User requested to remove memory, so we ignore history
        history = [] # data.get('history', [])
        
        print(f"\n--- Processing Query: '{question}' ---")
        
        # ============================================================
        # STEP 1: ROUTER - Classify intent and extract terms
        # ============================================================
        print("Step 1: Router - Classifying intent...")
        
        history_text = format_history_for_llm(history)
        router_prompt = ROUTER_PROMPT_TEMPLATE.format(
            question=question,
            history=history_text
        )
        
        router_response = generate(router_prompt)
        router_result = extract_json_from_response(router_response)
        
        intent = router_result.get('intent', 'OUT_OF_CONTEXT')
        terms = router_result.get('terms')
        
        print(f"Router Result: intent={intent}, terms={terms}")
        
        # Handle OUT_OF_CONTEXT
        if intent == 'OUT_OF_CONTEXT':
            return jsonify({
                "answer": "I apologize, but that question is outside my knowledge domain. I can only answer questions about Varma Kalai points, their locations, applications, and related symptoms.",
                "sources": [],
                "confidence": 0.0
            })
        
        # ============================================================
        # STEP 2: FETCH - Get full JSON context from database
        # ============================================================
        print("Step 2: Fetch - Retrieving data from database...")
        
        context_data = retriever.fetch_data(terms, intent)
        
        if not context_data:
            return jsonify({
                "answer": f"I apologize, but I could not find any information about '{terms}' in my database.",
                "sources": [],
                "confidence": 0.0
            })
        
        print(f"Fetched {len(context_data)} records")
        
        # ============================================================
        # STEP 3: GENERATE - Answer using context + chat history
        # ============================================================
        print("Step 3: Generate - Creating answer with LLM...")
        
        # Format context for LLM
        context_text = ""
        for i, point in enumerate(context_data, 1):
            context_text += f"\n[VARMA POINT {i}]\n"
            context_text += json.dumps(point, indent=2, ensure_ascii=False)
            context_text += "\n"
        
        # Generate answer
        generator_prompt = GENERATOR_PROMPT_TEMPLATE.format(
            context=context_text,
            history=history_text,
            question=question
        )
        
        answer = generate(generator_prompt)
        
        print("Answer generated successfully")
        
        # Extract source point names
        sources = [point.get('varmaName', 'Unknown') for point in context_data]
        
        return jsonify({
            "answer": answer,
            "sources": sources,
            "confidence": 1.0,
            "debug_intent": intent,
            "debug_terms": terms
        })
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "answer": "I apologize, but I encountered an error processing your request.",
            "sources": [],
            "confidence": 0.0,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
