import os
import json
import pickle
import glob
import sys
from pathlib import Path
import numpy as np

# 1. Setup Path to allow imports from 'src'
# We need 'backend/src/rag' in sys.path
current_file = Path(__file__).resolve()
ingestion_dir = current_file.parent             # backend/src/rag/src/ingestion
src_dir = ingestion_dir.parent                  # backend/src/rag/src
rag_root = src_dir.parent                       # backend/src/rag

sys.path.insert(0, str(rag_root))

try:
    from src.embeddings.embedder import VarmaEmbedder
    import faiss
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"sys.path: {sys.path}")
    print("Please run: pip install sentence_transformers faiss-cpu")
    sys.exit(1)

def load_documents(data_dir: str):
    """
    Load documents from JSON and TXT files in the data directory.
    Handles multiple JSON schemas.
    """
    documents = []
    
    # 1. Load JSON files
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    for jf in json_files:
        filename = os.path.basename(jf)
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Schema A: Standard "varmas" list (varma_data.json)
            if isinstance(data, dict) and "varmas" in data:
                print(f"Processing JSON (Standard): {filename}")
                for item in data["varmas"]:
                    anatomy = item.get("anatomicalRelations", {})
                    text = (
                        f"Varma Name: {item.get('varmaName', '')}\n"
                        f"Signs: {item.get('signs', '')}\n"
                        f"Pathognomic Sign: {item.get('pathognomicSign', '')}\n"
                        f"Indications: {item.get('indications', '')}\n"
                        f"Location: {item.get('surfaceAnatomy', '')}\n"
                        f"Tamil Literature: {item.get('tamilLiterature', '')}\n"
                        f"Varmam Type: {item.get('varmamType', '')}\n"
                        f"Anatomy: {anatomy}\n"
                    )
                    documents.append({"id": item.get("varmaName", "Unknown"), "text": text, "source": filename})

            # Schema B: Symptom to Varma Dict (02_symptom_to_varma.json)
            # Structure: {"headache": ["Point A", "Point B"], ...}
            elif isinstance(data, dict) and not "varmas" in data and not isinstance(list(data.values())[0], list) == False: 
                 # Heuristic: keys are strings, values are lists of strings
                print(f"Processing JSON (Symptom Map): {filename}")
                for key, val in data.items():
                    if isinstance(val, list):
                        text = f"Symptom: {key}\nRelated Varma Points: {', '.join(val)}"
                        documents.append({"id": f"symptom_{key}", "text": text, "source": filename})
            
            # Schema C: Varma to Symptom Dict (02_varma_to_symptom.json)
            # Structure: {"Utchi_Varmam": ["headache", "fever"], ...}
            # (Identical structure to B, but contextually different. The generic parser handles it well)

            # Schema D: List of Objects (01_preprocessed_symptoms.json)
            elif isinstance(data, list):
                print(f"Processing JSON (List): {filename}")
                for idx, item in enumerate(data):
                    # Specialized for 01_preprocessed
                    if "varma_point_name" in item and "symptom_text_raw" in item:
                        text = (
                            f"Varma Point: {item['varma_point_name']}\n"
                            f"Symptoms Summary: {item['symptom_text_raw']}"
                        )
                        documents.append({"id": f"pre_{item['varma_point_name']}_{idx}", "text": text, "source": filename})
                    else:
                        # Fallback for generic lists
                        text = json.dumps(item, indent=2)
                        documents.append({"id": f"{filename}_{idx}", "text": text, "source": filename})

        except Exception as e:
            print(f"Error loading {filename}: {e}")

    # 2. Load TXT files
    txt_files = glob.glob(os.path.join(data_dir, "*.txt"))
    for tf in txt_files:
        try:
            with open(tf, "r", encoding="utf-8") as f:
                text = f.read()
                if text.strip():
                    documents.append({
                        "id": os.path.basename(tf),
                        "text": text,
                        "source": os.path.basename(tf)
                    })
                    print(f"Processing TXT: {tf}")
        except Exception as e:
            print(f"Error loading {tf}: {e}")

    return documents

def build_index():
    # Expected data location: backend/src/rag/data
    # We are in backend/src/rag/src/ingestion
    # Data is in backend/src/rag/data
    data_dir = rag_root / "data"
    output_path = rag_root / "varma_index.pkl"
    
    print(f"Scanning Data Directory: {data_dir}")
    
    docs = load_documents(str(data_dir))
    print(f"Found {len(docs)} documents.")
    
    if not docs:
        print("No documents found. Exiting.")
        return

    print("Generating embeddings...")
    embedder = VarmaEmbedder()
    texts = [d["text"] for d in docs]
    embeddings = embedder.encode(texts)
    
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    with open(output_path, "wb") as f:
        pickle.dump((index, docs), f)
        
    print(f"Index string saved to {output_path}")

if __name__ == "__main__":
    build_index()
