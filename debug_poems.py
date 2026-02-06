
import sys
import os
import pandas as pd
from pathlib import Path

# Mock normalization
def _normalize_text(text):
    if not isinstance(text, str): return ""
    return "".join(c for c in text.lower() if c.isalnum())

def test_loading():
    print("--- DIAGNOSTICS START ---")
    file_path = Path("backend/data/raw/Varma_Points.xlsx")
    if not file_path.exists():
        print(f"FAIL: File not found at {file_path}")
        return

    try:
        df = pd.read_excel(file_path)
        print(f"PASS: Read Excel file. Raw Columns: {df.columns.tolist()}")
        
        # Apply the exact logic from app.py
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        name_col = "VARMAM_POINTS"
        poem_col = "TAMIL_LITERATURE"
        
        if name_col not in df.columns or poem_col not in df.columns:
            print(f"FAIL: Columns not found. Normalized: {df.columns.tolist()}")
            return
            
        print(f"PASS: Found columns '{name_col}' and '{poem_col}'")
        
        found_poems = 0
        for _, row in df.iterrows():
            if pd.isna(row[name_col]): continue
            poem = row[poem_col]
            if pd.isna(poem): continue
            
            s_poem = str(poem).strip()
            if len(s_poem) > 10:
                print(f"SAMPLE POEM ({row[name_col]}): {s_poem[:50]}...")
                found_poems += 1
                if found_poems >= 3: break
        
        print(f"--- DIAGNOSTICS COMPLETE: Found {found_poems} valid poems ---")

    except Exception as e:
        print(f"FAIL: Exception reading file: {e}")

if __name__ == "__main__":
    test_loading()
