"""
RAG API Routes for Varma Intelligence System
Integrates with your main Flask/FastAPI backend
"""
from flask import Blueprint, request, jsonify
import time
from pathlib import Path

# Create Blueprint for RAG routes
rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# Import your RAG components
from src.main.scoring_and_retrieval import VarmaRetriever, compute_confidence

# Initialize retriever (lazy loading)
_retriever = None

def get_retriever():
    """Lazy initialization of retriever"""
    global _retriever
    if _retriever is None:
        # Get paths relative to this file
        RAG_DIR = Path(__file__).resolve().parent
        DATA_DIR = RAG_DIR / "data" / "processed" / "intermediate_outputs"
        VARMA_SYMPTOMS_JSON = DATA_DIR / "02_varma_to_symptom.json"
        SYMPTOM_TO_VARMA_JSON = DATA_DIR / "02_symptom_to_varma.json"
        
        print("\n" + "="*80)
        print("INITIALIZING VARMA RAG RETRIEVER")
        print("="*80)
        
        try:
            _retriever = VarmaRetriever(
                varma_symptoms_path=VARMA_SYMPTOMS_JSON,
                symptom_to_varma_path=SYMPTOM_TO_VARMA_JSON
            )
            print("✓ RAG Retriever initialized successfully!")
        except Exception as e:
            print(f"✗ Failed to initialize retriever: {e}")
            raise
    
    return _retriever


@rag_bp.route('/health', methods=['GET'])
def rag_health_check():
    """Health check for RAG system"""
    try:
        retriever = get_retriever()
        return jsonify({
            "status": "healthy",
            "message": "Varma RAG system is running",
            "retriever_loaded": retriever is not None
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@rag_bp.route('/symptom-search', methods=['POST'])
def symptom_search():
    """Search Varma points by symptoms"""
    try:
        retriever = get_retriever()
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
        
        symptom_query = data['query'].strip()
        
        if not symptom_query:
            return jsonify({"error": "Empty query"}), 400
        
        print(f"\n{'='*80}")
        print(f"PROCESSING RAG QUERY: '{symptom_query}'")
        print(f"{'='*80}")
        
        # Track processing time
        start_time = time.perf_counter()
        
        # Call retrieval system
        result = retriever.retrieve(
            query=symptom_query,
            top_symptoms=15,
            top_varmas=5,
            lexical_threshold=0.45,
            semantic_threshold=0.55,
            verification_threshold=0.3
        )
        
        elapsed_time = time.perf_counter() - start_time
        
        # Format response for UI
        response = format_for_ui(result, symptom_query, elapsed_time)
        
        print(f"✓ Query processed in {elapsed_time:.3f}s")
        print(f"✓ Found {len(response['varma_points'])} Varma points")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"✗ Error processing query: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Import LLM Generator
from .src.llm.generator import generate

@rag_bp.route('/query', methods=['POST'])
def rag_query():
    """RAG question answering endpoint"""
    try:
        retriever = get_retriever()
        
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({"error": "Empty question"}), 400
        
        print(f"\nRAG Question: {question}")
        
        # Retrieve relevant documents
        result = retriever.retrieve(
            query=question,
            top_symptoms=10,
            top_varmas=3
        )
        
        # Format context for LLM
        varma_points = result.get("varma_points", [])
        context_parts = []
        for vp in varma_points:
            name = vp.get("varma_name", "Unknown")
            symptoms = ", ".join(vp.get("all_symptoms", []))
            desc = get_description_for_varma(name, vp.get("all_symptoms", []))
            context_parts.append(f"Varma Point: {name}\nDescription: {desc}\nSymptoms treated: {symptoms}\n")
        
        context_str = "\n".join(context_parts)
        
        # Construct Prompt
        prompt = f"""You are an expert in Varma Kalai (an ancient Indian martial art and healing system). 
Use the following retrieved context to answer the user's question. 
If the answer is not in the context, use your general knowledge but mention that it is general info.

Context:
{context_str}

User Question: {question}

Answer:"""

        print("Generating answer with LLM...")
        # Call Ollama
        llm_response = generate(prompt, model="llama3")
        print("LLM Response received.")

        # Format as RAG response
        response = {
            "answer": llm_response,
            "sources": extract_sources(result),
            "confidence": calculate_overall_confidence(result)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"✗ RAG Query Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@rag_bp.route('/varma-points', methods=['GET'])
def get_all_varma_points():
    """Get all available Varma points"""
    try:
        retriever = get_retriever()
        
        all_points = []
        for varma_name in retriever.varma_data.keys():
            all_points.append({
                "name": varma_name,
                "category": categorize_varma(varma_name),
                "location": get_location_for_varma(varma_name)
            })
        
        return jsonify({"varma_points": all_points}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Helper functions
def format_for_ui(result, query, processing_time):
    """Transform retrieval result for React UI"""
    varma_points = result.get("varma_points", [])
    matched_symptoms = result.get("matched_symptoms", [])
    
    formatted_points = []
    
    for idx, vp in enumerate(varma_points):
        weighted_score = vp.get("weighted_score", 0.0)
        confidence_score = compute_confidence(
            weighted_score=weighted_score,
            scale=5.0
        )
        
        if vp.get("exact_count", 0) > 0:
            primary_match_type = "lexical_exact"
        elif vp.get("verified_count", 0) > 0:
            primary_match_type = "semantic_verified"
        else:
            primary_match_type = "semantic_partial"
        
        matched_syms = vp.get("matched_symptoms", [])
        all_syms = vp.get("all_symptoms", [])
        
        formatted_point = {
            "id": vp.get("varma_id", f"vp_{idx+1:03d}"),
            "name": vp.get("varma_name", "Unknown"),
            "confidence_score": round(confidence_score, 4),
            "match_type": primary_match_type,
            "location": get_location_for_varma(vp.get("varma_name", "")),
            "matched_symptoms": matched_syms,
            "all_symptoms": all_syms,
            "coordinates": get_coordinates_for_varma(vp.get("varma_name", "")),
            "description": get_description_for_varma(vp.get("varma_name", ""), all_syms),
            "category": categorize_varma(vp.get("varma_name", "")),
            "treatment_methods": get_treatment_methods(vp.get("varma_name", "")),
            "contraindications": get_contraindications(vp.get("varma_name", "")),
            "matched_symptom_count": vp.get("matched_symptom_count", 0),
            "total_symptoms": vp.get("total_symptoms", 0),
            "match_percentage": vp.get("match_percentage", 0.0),
            "weighted_score": round(vp.get("weighted_score", 0.0), 2),
            "exact_count": vp.get("exact_count", 0),
            "verified_count": vp.get("verified_count", 0),
            "partial_count": vp.get("partial_count", 0),
            "avg_match_quality": round(vp.get("avg_match_quality", 0.0), 4)
        }
        
        formatted_points.append(formatted_point)
    
    total_points = len(formatted_points)
    avg_confidence = sum(p['confidence_score'] for p in formatted_points) / total_points if total_points > 0 else 0
    
    match_type_counts = {}
    for p in formatted_points:
        mt = p['match_type']
        match_type_counts[mt] = match_type_counts.get(mt, 0) + 1
    
    response = {
        "query": query,
        "varma_points": formatted_points,
        "statistics": {
            "total_points": total_points,
            "average_confidence": round(avg_confidence, 4),
            "match_types": match_type_counts,
            "processing_time_ms": round(processing_time * 1000, 2)
        },
        "matched_symptoms_details": [
            {
                "symptom": ms.get("symptom", ""),
                "score": round(ms.get("combined_score", 0.0), 4),
                "match_type": ms.get("match_type", "")
            }
            for ms in matched_symptoms
        ]
    }
    
    return response


def generate_answer_from_results(result, question):
    """Generate natural language answer from retrieval results"""
    varma_points = result.get("varma_points", [])
    
    if not varma_points:
        return "I couldn't find specific Varma points related to your question. Could you rephrase or provide more details?"
    
    answer_parts = [f"Based on your question about '{question}', here's what I found:\n"]
    
    for idx, vp in enumerate(varma_points[:3], 1):
        varma_name = vp.get("varma_name", "Unknown")
        symptoms = vp.get("all_symptoms", [])
        
        answer_parts.append(f"\n{idx}. **{varma_name}**")
        if symptoms:
            answer_parts.append(f"   - Associated with: {', '.join(symptoms[:5])}")
        answer_parts.append(f"   - Match confidence: {vp.get('weighted_score', 0):.2f}")
    
    return "\n".join(answer_parts)


def extract_sources(result):
    """Extract source information"""
    varma_points = result.get("varma_points", [])
    return [vp.get("varma_name", "Unknown") for vp in varma_points[:5]]


def calculate_overall_confidence(result):
    """Calculate overall confidence score"""
    varma_points = result.get("varma_points", [])
    if not varma_points:
        return 0.0
    
    scores = [vp.get("weighted_score", 0.0) for vp in varma_points]
    return round(sum(scores) / len(scores), 4)


def get_description_for_varma(varma_name, all_symptoms):
    """Get description for Varma point"""
    if all_symptoms and len(all_symptoms) > 0:
        symptoms_text = ", ".join(all_symptoms[:10])
        return f"This Varma point is associated with {len(all_symptoms)} signs and symptoms including: {symptoms_text}"
    return f"Traditional Varma point '{varma_name}' with therapeutic significance."


def get_location_for_varma(varma_name):
    """Map Varma names to body locations"""
    location_map = {
        "adhipathi": "Crown of the head",
        "shankha": "Temple region",
        "krikatika": "Back of the neck",
        "sthapani": "Between the eyebrows",
        "hridaya": "Heart region",
        "nabhi": "Navel region",
        "janu": "Knee joint",
        "gulpha": "Ankle joint"
    }
    
    varma_lower = varma_name.lower()
    for key, location in location_map.items():
        if key in varma_lower:
            return location
    
    return "Body region"


def get_coordinates_for_varma(varma_name):
    """Generate coordinates for 3D visualization"""
    coord_map = {
        "adhipathi": {"x": 100, "y": 40},
        "shankha": {"x": 70, "y": 45},
        "hridaya": {"x": 100, "y": 120},
        "nabhi": {"x": 100, "y": 160},
        "janu": {"x": 85, "y": 240}
    }
    
    varma_lower = varma_name.lower()
    for key, coords in coord_map.items():
        if key in varma_lower:
            return coords
    
    import random
    return {"x": random.randint(50, 150), "y": random.randint(80, 250)}


def categorize_varma(varma_name):
    """Categorize Varma by body region"""
    varma_lower = varma_name.lower()
    
    if any(term in varma_lower for term in ['adhipathi', 'shankha', 'sthapani']):
        return "Head & Neck"
    elif any(term in varma_lower for term in ['hridaya', 'kurpara']):
        return "Upper Body"
    elif any(term in varma_lower for term in ['nabhi', 'basti']):
        return "Abdomen & Pelvis"
    elif any(term in varma_lower for term in ['janu', 'gulpha']):
        return "Lower Body"
    return "General"


def get_treatment_methods(varma_name):
    """Get treatment methods"""
    return [
        "Gentle pressure application",
        "Herbal oil massage",
        "Therapeutic manipulation"
    ]


def get_contraindications(varma_name):
    """Get contraindications"""
    return [
        "Acute injury or inflammation",
        "Open wounds in the area",
        "Consult practitioner for chronic conditions"
    ]