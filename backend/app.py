from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main.scoring_and_retrieval import VarmaRetriever, compute_confidence
from src.main.lexical_matching import _normalize_text
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app)

# Initialize retriever once at startup
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate_outputs"
VARMA_SYMPTOMS_JSON = DATA_DIR / "02_varma_to_symptom.json"
SYMPTOM_TO_VARMA_JSON = DATA_DIR / "02_symptom_to_varma.json"

print("\n" + "="*80)
print("INITIALIZING VARMA RETRIEVAL SYSTEM")
print("="*80)

try:
    retriever = VarmaRetriever(
        varma_symptoms_path=VARMA_SYMPTOMS_JSON,
        symptom_to_varma_path=SYMPTOM_TO_VARMA_JSON
    )
    print("\n✓ Retriever initialized successfully!")
except FileNotFoundError as fnf_error:
    print(f"\n✗ CRITICAL: Missing data file! {fnf_error}")
    print(f"Ensure that '{VARMA_SYMPTOMS_JSON}' and '{SYMPTOM_TO_VARMA_JSON}' exist.")
    retriever = None
except Exception as e:
    print(f"\n✗ Failed to initialize retriever: {e}")
    retriever = None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Varma Intelligence Backend is running",
        "retriever_loaded": retriever is not None
    })

@app.route('/api/symptom-search', methods=['POST'])
def symptom_search():
    if retriever is None:
        return jsonify({"error": "Retriever not initialized"}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
        
        symptom_query = data['query'].strip()
        
        if not symptom_query:
            return jsonify({"error": "Empty query"}), 400
        
        print(f"\n{'='*80}")
        print(f"PROCESSING QUERY: '{symptom_query}'")
        print(f"{'='*80}")
        
        # Track processing time
        start_time = time.perf_counter()
        
        # Call your retrieval system
        result = retriever.retrieve(
            query=symptom_query,
            top_symptoms=15,
            top_varmas=5,
            lexical_threshold=0.45,
            semantic_threshold=0.55,
            verification_threshold=0.3
        )
        
        elapsed_time = time.perf_counter() - start_time
        
        # Format response for React UI
        response = format_for_ui(result, symptom_query, elapsed_time)
        
        print(f"\n✓ Query processed in {elapsed_time:.3f}s")
        print(f"✓ Found {len(response['varma_points'])} Varma points")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"\n✗ Error processing query: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# RAG Service has been moved to rag_service.py (Port 5004)


def format_for_ui(result, query, processing_time):
    """
    Transform your retrieval result into the format expected by React UI
    """
    
    varma_points = result.get("varma_points", [])
    matched_symptoms = result.get("matched_symptoms", [])
    
    formatted_points = []
    
    for idx, vp in enumerate(varma_points):
        # Calculate confidence score
        weighted_score = vp.get("weighted_score", 0.0)
        confidence_score = compute_confidence(
            weighted_score=weighted_score,
            scale=5.0
        )
        
        # Determine match type based on counts
        if vp.get("exact_count", 0) > 0:
            primary_match_type = "lexical_exact"
        elif vp.get("verified_count", 0) > 0:
            primary_match_type = "semantic_verified"
        else:
            primary_match_type = "semantic_partial"
        
        # Get matched symptoms for this Varma point
        matched_syms = vp.get("matched_symptoms", [])
        
        # Get ALL symptoms for this Varma point from dataset
        all_syms = vp.get("all_symptoms", [])
        
        formatted_point = {
            "id": vp.get("varma_id", f"vp_{idx+1:03d}"),
            "name": vp.get("varma_name", "Unknown"),
            "confidence_score": round(confidence_score, 4),
            "match_type": primary_match_type,
            "location": get_location_for_varma(vp.get("varma_name", "")),
            "matched_symptoms": matched_syms,  # ALL matched symptoms (no limit)
            "all_symptoms": all_syms,  # ALL symptoms from dataset (no limit)
            "coordinates": get_coordinates_for_varma(vp.get("varma_name", "")),
            "description": get_description_for_varma_with_data(vp.get("varma_name", ""), all_syms),
            "category": categorize_varma(vp.get("varma_name", "")),
            "treatment_methods": get_treatment_methods(vp.get("varma_name", "")),
            "contraindications": get_contraindications(vp.get("varma_name", "")),
            
            # Additional metadata
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
    
    # Calculate statistics
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
            for ms in matched_symptoms  # ALL symptoms (no limit)
        ]
    }
    
    return response

def get_description_for_varma_with_data(varma_name, all_symptoms):
    """Provide descriptions for Varma points from actual dataset symptoms - shows ALL"""
    
    if all_symptoms and isinstance(all_symptoms, list) and len(all_symptoms) > 0:
        # Show ALL symptoms without limiting
        symptoms_text = ", ".join(all_symptoms)
        return f"This Varma point is associated with {len(all_symptoms)} signs and symptoms including: {symptoms_text}"
    
    # Fallback if no symptoms available
    return f"Traditional Varma point '{varma_name}' with therapeutic significance in Siddha medicine."

def get_location_for_varma(varma_name):
    """Map Varma point names to body locations"""
    location_map = {
        "adhipathi": "Crown of the head",
        "shankha": "Temple region (both sides)",
        "krikatika": "Back of the neck",
        "sthapani": "Between the eyebrows",
        "apanga": "Outer corner of the eye",
        "phana": "Nostril region",
        "vidhura": "Behind the ear",
        "hridaya": "Heart region",
        "nabhi": "Navel region",
        "basti": "Lower abdomen",
        "guda": "Rectal region",
        "lohitaksha": "Armpit",
        "kakshadhara": "Shoulder region",
        "kurpara": "Elbow joint",
        "manibandha": "Wrist joint",
        "kshipra": "Between thumb and index finger",
        "tala": "Palm center",
        "vitapa": "Groin region",
        "janu": "Knee joint",
        "gulpha": "Ankle joint",
        "pada": "Foot region"
    }
    
    varma_lower = varma_name.lower()
    for key, location in location_map.items():
        if key in varma_lower:
            return location
    
    return "Body region (location varies)"

def get_coordinates_for_varma(varma_name):
    """Generate approximate coordinates for 3D visualization"""
    coord_map = {
        "adhipathi": {"x": 100, "y": 40},
        "shankha": {"x": 70, "y": 45},
        "krikatika": {"x": 100, "y": 80},
        "sthapani": {"x": 100, "y": 50},
        "hridaya": {"x": 100, "y": 120},
        "nabhi": {"x": 100, "y": 160},
        "basti": {"x": 100, "y": 180},
        "lohitaksha": {"x": 50, "y": 100},
        "kurpara": {"x": 40, "y": 130},
        "manibandha": {"x": 30, "y": 160},
        "janu": {"x": 85, "y": 240},
        "gulpha": {"x": 85, "y": 280}
    }
    
    varma_lower = varma_name.lower()
    for key, coords in coord_map.items():
        if key in varma_lower:
            return coords
    
    import random
    return {"x": random.randint(50, 150), "y": random.randint(80, 250)}

def categorize_varma(varma_name):
    """Categorize Varma points by body region"""
    varma_lower = varma_name.lower()
    
    if any(term in varma_lower for term in ['adhipathi', 'shankha', 'sthapani', 'krikatika', 'apanga', 'phana', 'vidhura']):
        return "Head & Neck"
    elif any(term in varma_lower for term in ['hridaya', 'lohitaksha', 'kakshadhara', 'kurpara', 'manibandha']):
        return "Upper Body"
    elif any(term in varma_lower for term in ['nabhi', 'basti', 'guda', 'vitapa']):
        return "Abdomen & Pelvis"
    elif any(term in varma_lower for term in ['janu', 'gulpha', 'pada']):
        return "Lower Body"
    else:
        return "General"

def get_treatment_methods(varma_name):
    """Provide treatment methods"""
    return [
        "Gentle pressure application",
        "Herbal oil massage",
        "Therapeutic manipulation"
    ]

def get_contraindications(varma_name):
    """Provide contraindications"""
    return [
        "Acute injury or inflammation",
        "Open wounds in the area",
        "Consult practitioner for chronic conditions"
    ]

@app.route('/api/varma-points', methods=['GET'])
def get_all_varma_points():
    """Get all available Varma points (for future use)"""
    if retriever is None:
        return jsonify({"error": "Retriever not initialized"}), 500
    
    try:
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

if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTING VARMA INTELLIGENCE BACKEND")
    print("="*80)
    print(f"Server will run at: http://localhost:5003")
    print(f"API endpoint: http://localhost:5003/api/symptom-search")
    print("="*80 + "\n")
    
    app.run(debug=True, port=5003, host='0.0.0.0')