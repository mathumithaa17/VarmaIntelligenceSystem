import sys
import json
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main.lexical_matching import _normalize_text

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXCEL_PATH = PROJECT_ROOT / "data" / "raw" / "Varma_Points.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "intermediate_outputs"

print("\n" + "="*80)
print("REGENERATING JSON FROM EXCEL FILE")
print("="*80)
print(f"Excel File: {EXCEL_PATH}")
print(f"Output Dir: {OUTPUT_DIR}")

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

try:
    # Load Excel file
    df = pd.read_excel(EXCEL_PATH)
    
    # Normalize column names
    df.columns = [str(c).strip().upper() for c in df.columns]
    print(f"\n✓ Excel Columns: {df.columns.tolist()}")
    
    # Identify columns
    name_col = "VARMAM_POINTS"
    poem_col = "TAMIL_LITERATURE"
    
    if name_col not in df.columns:
        name_col = next((c for c in df.columns if 'NAME' in c or 'POINT' in c), None)
    
    if poem_col not in df.columns:
        poem_col = next((c for c in df.columns if 'LITERATURE' in c or 'POEM' in c), None)
    
    print(f"✓ Using Name Column: {name_col}")
    print(f"✓ Using Poem Column: {poem_col}")
    
    # Build data structures
    varma_to_symptom = {}  # varma -> [symptoms]
    symptom_to_varma = {}  # symptom -> [varmas]
    
    for _, row in df.iterrows():
        if pd.isna(row[name_col]):
            continue
        
        varma_name = str(row[name_col]).strip()
        norm_varma = _normalize_text(varma_name)
        
        # Get symptoms if column exists
        symptoms = []
        symptom_col = next((c for c in df.columns if 'SYMPTOM' in c or 'SIGN' in c), None)
        
        if symptom_col and not pd.isna(row[symptom_col]):
            symptom_text = str(row[symptom_col]).strip()
            symptoms = [s.strip() for s in symptom_text.split(',') if s.strip()]
        
        # Build varma_to_symptom mapping
        varma_to_symptom[norm_varma] = {
            "varma_name": varma_name,
            "symptoms": symptoms,
            "poem": str(row[poem_col]).strip() if poem_col and not pd.isna(row[poem_col]) else ""
        }
        
        # Build symptom_to_varma mapping
        for symptom in symptoms:
            norm_symptom = _normalize_text(symptom)
            if norm_symptom not in symptom_to_varma:
                symptom_to_varma[norm_symptom] = {
                    "symptom_name": symptom,
                    "varmas": []
                }
            symptom_to_varma[norm_symptom]["varmas"].append(norm_varma)
    
    # Save to JSON files
    varma_to_symptom_path = OUTPUT_DIR / "02_varma_to_symptom.json"
    symptom_to_varma_path = OUTPUT_DIR / "02_symptom_to_varma.json"
    
    with open(varma_to_symptom_path, 'w', encoding='utf-8') as f:
        json.dump(varma_to_symptom, f, ensure_ascii=False, indent=2)
    
    with open(symptom_to_varma_path, 'w', encoding='utf-8') as f:
        json.dump(symptom_to_varma, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved {len(varma_to_symptom)} Varma points to {varma_to_symptom_path}")
    print(f"✓ Saved {len(symptom_to_varma)} Symptoms to {symptom_to_varma_path}")
    print("\n" + "="*80)
    print("✓ JSON FILES REGENERATED SUCCESSFULLY!")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()