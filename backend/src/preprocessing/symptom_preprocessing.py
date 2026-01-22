import pandas as pd
import json
import re
from pathlib import Path

RAW_PATH = Path("data/raw/Varma_Points.xlsx")
OUT_DIR = Path("data/processed/intermediate_outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = OUT_DIR / "01_preprocessed_symptoms.json"

REQUIRED_COLS = ["VARMAM_POINTS", "SIGNS", "PATHOGNOMIC_SIGN"]

def generate_varma_id(index: int) -> str:
    return f"VP{index+1:03d}"

def clean_and_split_symptoms(text: str):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9,\s]", " ", text)
    tokens = [s.strip() for s in text.split(",")]
    return [t for t in tokens if t]

def process():
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Excel file not found at: {RAW_PATH}")

    df = pd.read_excel(RAW_PATH)
    print("Loaded rows:", len(df))
    print("Columns detected:", list(df.columns))

    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise KeyError(f"Required column missing: {col}")

    processed = []

    for idx, row in df.iterrows():
        vp_id = generate_varma_id(idx)

        signs = str(row["SIGNS"]).strip()
        pathognomic = str(row["PATHOGNOMIC_SIGN"]).strip()

        combined_symptoms = f"{signs}, {pathognomic}".strip()
        symptom_tokens = clean_and_split_symptoms(combined_symptoms)

        processed.append({
            "varma_point_id": vp_id,
            "varma_point_name": str(row["VARMAM_POINTS"]).strip(),
            "symptom_text_raw": combined_symptoms,
            "symptom_tokens": symptom_tokens
        })

    OUTPUT_JSON.write_text(
        json.dumps(processed, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Saved preprocessed dataset → {OUTPUT_JSON}")

if __name__ == "__main__":
    process()
