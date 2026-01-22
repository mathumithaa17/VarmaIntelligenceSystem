from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import time
from pathlib import Path

# Add src to path so we can import internal modules
sys.path.insert(0, str(Path(__file__).parent))

from src.main.scoring_and_retrieval import VarmaRetriever, compute_confidence
from src.rag.src.llm.generator import generate

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# ==============================================================================
# INITIALIZATION
# ==============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate_outputs"
VARMA_SYMPTOMS_JSON = DATA_DIR / "02_varma_to_symptom.json"
SYMPTOM_TO_VARMA_JSON = DATA_DIR / "02_symptom_to_varma.json"

print("\n" + "="*80)
print("INITIALIZING RAG SERVICE (PORT 5004)")
print("="*80)

retriever = None
try:
    retriever = VarmaRetriever(
        varma_symptoms_path=VARMA_SYMPTOMS_JSON,
        symptom_to_varma_path=SYMPTOM_TO_VARMA_JSON
    )
    print("\n✓ RAG Retriever initialized successfully!")
except Exception as e:
    print(f"\n✗ Failed to initialize retriever: {e}")


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def extract_sources(result):
    varma_points = result.get("varma_points", [])
    return [vp.get("varma_name", "Unknown") for vp in varma_points[:5]]

def calculate_overall_confidence(result):
    varma_points = result.get("varma_points", [])
    if not varma_points: return 0.0
    scores = [vp.get("weighted_score", 0.0) for vp in varma_points]
    return round(sum(scores) / len(scores), 4)

def get_description_for_varma(varma_name, all_symptoms):
    if all_symptoms and len(all_symptoms) > 0:
        symptoms_text = ", ".join(all_symptoms[:10])
        return f"This Varma point is associated with {len(all_symptoms)} signs and symptoms including: {symptoms_text}"
    return f"Traditional Varma point '{varma_name}' with therapeutic significance."

def generate_fallback_answer(question, result):
    """
    Generates a rule-based answer when LLM is offline.
    Uses regex/keywords to answer common 'What is' questions.
    """
    q_lower = question.lower()
    varma_points = result.get("varma_points", [])
    
    # 1. Definition of Varma Kalai (Added "what are varma")
    if any(x in q_lower for x in ["what is varma", "what are varma", "define varma", "varma kalai", "about varma"]):
        return (
            "**Varma Kalai** is an ancient Indian martial art and healing science that originated in Tamil Nadu. "
            "It focuses on vital points (Varmams) in the body that can be manipulated for self-defense or therapeutic purposes. "
            "The system treats various ailments by stimulating these energy points to restore the flow of Prana (life energy).\n\n"
            "Here are some specific Varma points found in our database that might be relevant:"
        )
        
    # 2. General list query
    if "list" in q_lower or "how many" in q_lower or "points" in q_lower:
        return f"There are traditionally 108 vital Varma points. Based on your search, here are the top {len(varma_points)} relevant points found:"

    # 3. Specific Symptom query (heuristic)
    if "headache" in q_lower:
        return "For **headaches**, traditional Varma therapy often recommends points located on the head and neck regions. The following points are most relevant based on your query:"
    
    if "knee" in q_lower or "leg" in q_lower:
        return "For **leg or knee issues**, points like 'Janu Varma' (Knee) or 'Gulpha Varma' (Ankle) are typically indicated. Here are the matches from our database:"

    # Default fallback
    return (
        f"I found {len(varma_points)} Varma points that match your query. "
        "Since the AI model is currently offline, I cannot generate a detailed custom explanation, but here are the direct results from the Varma textbook data:"
    )

# ==============================================================================
# API ROUTES
# ==============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Varma RAG Service",
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
        
        print(f"\nRAG Question: {question}")
        
        # 1. Retrieve relevant documents
        result = retriever.retrieve(
            query=question,
            top_symptoms=10,
            top_varmas=3
        )
        
        # 2. Format context for LLM
        varma_points = result.get("varma_points", [])
        context_parts = []
        for vp in varma_points:
            name = vp.get("varma_name", "Unknown")
            symptoms = ", ".join(vp.get("all_symptoms", []))
            desc = get_description_for_varma(name, vp.get("all_symptoms", []))
            context_parts.append(f"Varma Point: {name}\nDescription: {desc}\nSymptoms treated: {symptoms}\n")
        
        context_str = "\n".join(context_parts)
        
        # 3. Construct Prompt
        prompt = f"""You are an expert in Varma Kalai (an ancient Indian martial art and healing system). 
Use the following retrieved context to answer the user's question. 
If the answer is not in the context, use your general knowledge but mention that it is general info.

Context:
{context_str}

User Question: {question}

Answer:"""

        print("Generating answer with LLM...")
        # 4. Call Ollama (with robust error handling inside generate)
        llm_response = generate(prompt, model="llama3")
        
        # Check if Ollama failed and we got the fallback message
        if llm_response.startswith("Note: Local LLM") or llm_response.startswith("Ollama error"):
            print("LLM unavailable, generating smart fallback...")
            fallback_answer = generate_fallback_answer(question, result)
            # Replace the error with the smart fallback and a subtle footer
            llm_response = fallback_answer + "\n\n*(Note: Running in offline mode. Install Ollama for detailed AI analysis.)*"
            
        print("LLM Response received.")

        # 5. Format response
        response = {
            "answer": llm_response,
            "sources": extract_sources(result),
            "confidence": calculate_overall_confidence(result)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"✗ RAG Query Error: {str(e)}")
        # Return proper error JSON instead of crashing
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTING VARMA RAG SERVICE")
    print("="*80)
    print(f"Service running at: http://localhost:5004")
    print("="*80 + "\n")
    
    app.run(debug=True, port=5004, host='0.0.0.0')
