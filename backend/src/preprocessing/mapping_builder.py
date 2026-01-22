import json
from pathlib import Path
from collections import defaultdict

INPUT_JSON = Path("data/processed/intermediate_outputs/01_preprocessed_symptoms.json")
OUT_DIR = Path("data/processed/intermediate_outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SYMPTOM_TO_VARMA_JSON = OUT_DIR / "02_symptom_to_varma.json"
VARMA_TO_SYMPTOM_JSON = OUT_DIR / "02_varma_to_symptom.json"
DEBUG_JSON = OUT_DIR / "02_mapping_debug.json"

def build_mappings():
    if not INPUT_JSON.exists():
        raise FileNotFoundError("01_preprocessed_symptoms.json not found.")

    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    symptom_to_varma = defaultdict(list)
    varma_to_symptom = defaultdict(list)
    debug_entries = []

    for entry in data:
        vp_id = entry["varma_point_id"]
        vp_name = entry["varma_point_name"]
        symptoms = entry["symptom_tokens"]  

        for symptom in symptoms:
            symptom = symptom.strip()
            if symptom == "":
                continue

            symptom_to_varma[symptom].append(vp_name)
            varma_to_symptom[vp_name].append(symptom)

            debug_entries.append({
                "varma_point_id": vp_id,
                "varma_point_name": vp_name,
                "symptom_phrase": symptom
            })

    symptom_to_varma = {k: list(set(v)) for k, v in symptom_to_varma.items()}
    varma_to_symptom = {k: list(set(v)) for k, v in varma_to_symptom.items()}

    SYMPTOM_TO_VARMA_JSON.write_text(json.dumps(symptom_to_varma, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved symptom → varma mapping → {SYMPTOM_TO_VARMA_JSON}")

    VARMA_TO_SYMPTOM_JSON.write_text(json.dumps(varma_to_symptom, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved varma → symptom mapping → {VARMA_TO_SYMPTOM_JSON}")

    print("\nMappings built successfully!")
    return symptom_to_varma, varma_to_symptom

if __name__ == "__main__":
    build_mappings()
