import json
import random
from pathlib import Path
from itertools import combinations

SYMPTOM_TO_VARMA_JSON = Path("data/processed/intermediate_outputs/02_symptom_to_varma.json")

OUT_DIR = Path("data/processed/intermediate_outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TESTSET_JSON = OUT_DIR / "03_test_dataset.json"
DEBUG_JSON = OUT_DIR / "03_test_dataset_debug.json"

QUERY_TEMPLATES = [
    "I have {symptoms}",
    "I am experiencing {symptoms}",
    "I feel {symptoms}",
    "I have been having {symptoms}",
    "I am suffering from {symptoms}",
    "I noticed {symptoms} recently"
]


def common_varma(symptom_list, symptom_to_varma):
    """Return common Varma points across symptoms"""
    sets = [set(symptom_to_varma[s]) for s in symptom_list]
    return list(set.intersection(*sets))


def format_symptoms(symptoms):
    """Convert list to natural language phrase"""
    if len(symptoms) == 1:
        return symptoms[0]
    if len(symptoms) == 2:
        return f"{symptoms[0]} and {symptoms[1]}"
    return ", ".join(symptoms[:-1]) + f", and {symptoms[-1]}"


def build_testset():
    print("\n========== BUILDING TEST DATASET ==========")

    if not SYMPTOM_TO_VARMA_JSON.exists():
        raise FileNotFoundError("02_symptom_to_varma.json not found.")

    symptom_to_varma = json.loads(
        SYMPTOM_TO_VARMA_JSON.read_text(encoding="utf-8")
    )

    symptoms = sorted(symptom_to_varma.keys())

    test_rows = []
    debug_rows = []
    test_id = 1

    for symptom in symptoms:
        template = random.choice(QUERY_TEMPLATES)
        query = template.format(symptoms=symptom)

        test_rows.append({
            "id": f"T{test_id:04d}",
            "symptom": query
        })

        debug_rows.append({
            "id": f"T{test_id:04d}",
            "query_type": "unigram",
            "symptoms": [symptom],
            "query": query,
            "varma_points_ground_truth": symptom_to_varma[symptom]
        })

        test_id += 1

    for n in [2, 3]:
        for combo in combinations(symptoms, n):
            common = common_varma(list(combo), symptom_to_varma)

            if not common:
                continue  

            phrase = format_symptoms(list(combo))
            template = random.choice(QUERY_TEMPLATES)
            query = template.format(symptoms=phrase)

            test_rows.append({
                "id": f"T{test_id:04d}",
                "symptom": query
            })

            debug_rows.append({
                "id": f"T{test_id:04d}",
                "query_type": "bigram" if n == 2 else "trigram",
                "symptoms": list(combo),
                "query": query,
                "varma_points_ground_truth": common
            })

            test_id += 1

    TESTSET_JSON.write_text(
        json.dumps(test_rows, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    DEBUG_JSON.write_text(
        json.dumps(debug_rows, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Saved CLEAN test dataset  → {TESTSET_JSON}")
    print(f"Saved DEBUG test dataset  → {DEBUG_JSON}")
    print(f"Total test cases created: {len(test_rows)}")
    print("\nTest dataset generated successfully!")

    return test_rows, debug_rows


if __name__ == "__main__":
    build_testset()