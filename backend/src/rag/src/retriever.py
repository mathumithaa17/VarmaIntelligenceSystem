import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any

class RuleBasedRetriever:
    """
    A strict rule-based retriever that uses local JSON files to answer Varma-related queries.
    It prioritizes:
    1. Symptom lookup -> linked Varma points
    2. Direct Varma point name lookup
    3. Rejection of unrelated queries
    """

    def __init__(self):
        # Define paths relative to this file: backend/src/rag/src/retriever.py
        
        self.base_path = Path(__file__).resolve().parent  # backend/src/rag/src
        
        # Path to varma_data.json (backend/src/rag/data/varma_data.json)
        self.varma_data_path = self.base_path.parent / "data" / "varma_data.json"
        
        # Path to symptom_to_varma.json (backend/data/processed/intermediate_outputs/02_symptom_to_varma.json)
        # Using parents[2] to go to 'backend' based on verification
        self.symptom_map_path = self.base_path.parents[2] / "data" / "processed" / "intermediate_outputs" / "02_symptom_to_varma.json"

        print(f"Loading Varma Data from: {self.varma_data_path}")
        print(f"Loading Symptom Map from: {self.symptom_map_path}")

        self.varma_db = []
        self.symptom_map = {}
        
        self.load_data()

    def load_data(self):
        """Loads JSON datasets into memory."""
        try:
            if self.varma_data_path.exists():
                with open(self.varma_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both list formats (raw list or dict with "varmas" key)
                    if isinstance(data, dict) and "varmas" in data:
                        self.varma_db = data["varmas"]
                    elif isinstance(data, list):
                        self.varma_db = data
                    else:
                        print(f"Warning: Unexpected format in varma_data.json")
            else:
                print(f"Error: varma_data.json not found at {self.varma_data_path}")

            if self.symptom_map_path.exists():
                with open(self.symptom_map_path, 'r', encoding='utf-8') as f:
                    self.symptom_map = json.load(f)
            else:
                print(f"Error: 02_symptom_to_varma.json not found at {self.symptom_map_path}")

        except Exception as e:
            print(f"Error loading rule-based data: {e}")

    def normalize(self, text: str) -> str:
        """Normalizes text for case-insensitive comparison."""
        if not text: return ""
        return text.lower().strip().replace("_", " ")

    def fetch_data(self, term: str, intent: str) -> List[Dict[str, Any]]:
        """
        Strict lookup based on LLM-extracted term.
        intent: 'SYMPTOM' or 'VARMA_POINT'
        """
        normalized_term = self.normalize(term)
        results = []

        if intent == "SYMPTOM":
            # 1. Try exact match in symptom map
            # We iterate because keys in map might differ in casing/spacing from normalized term
            # But self.symptom_map keys are raw.
            
            # Create a normalized map for lookup if not already efficient, 
            # but given size, iterating is okay or we can cache.
            # Let's use the logic we had: check if normalized_term matches any normalized key
            
            target_varma_names = set()
            
            # Quick lookup if keys were normalized. They aren't in self.symptom_map.
            # So we scan.
            for raw_sym, varma_list in self.symptom_map.items():
                if self.normalize(raw_sym) == normalized_term:
                    for v in varma_list:
                        target_varma_names.add(self.normalize(v))
            
            # Fetch details
            for point in self.varma_db:
                if self.normalize(point.get("varmaName", "")) in target_varma_names:
                    results.append(point)

        elif intent == "VARMA_POINT":
            # Search for exact Varma name match
            for point in self.varma_db:
                if self.normalize(point.get("varmaName", "")) == normalized_term:
                    results.append(point)
        
        return results

    def lookup(self, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Legacy lookup method. Kept for backward compatibility if needed, 
        but the new flow should use fetch_data.
        """
        # ... (existing lookup code)
        normalized_query = self.normalize(query)
        if not normalized_query:
            return None, []
        
        # Prepare collapsed query for fuzzy matching (e.g. "head ache" -> "headache")
        collapsed_query = normalized_query.replace(" ", "")

        normalized_symptoms = {self.normalize(k): k for k in self.symptom_map.keys()}
        
        # 1. Direct Varma Point Lookup
        found_points = []
        for point in self.varma_db:
            point_name = point.get("varmaName", "")
            norm_name = self.normalize(point_name)
            
            # Check standard match or collapsed match
            if norm_name in normalized_query:
                found_points.append(point)
            elif len(norm_name) > 4 and norm_name.replace(" ", "") in collapsed_query:
                found_points.append(point)
        
        if found_points:
            return "varma_point", found_points

        # 2. Symptom Lookup
        matched_symptoms = []
        # Sort symptoms by length (longest first)
        sorted_symptom_keys = sorted(normalized_symptoms.keys(), key=len, reverse=True)
        
        for norm_sym in sorted_symptom_keys:
            original_sym = normalized_symptoms[norm_sym]
            
            # Check 1: Standard inclusion ("headache" in "i have a headache")
            if norm_sym in normalized_query:
                 matched_symptoms.append(original_sym)
                 continue

            # Check 2: Collapsed inclusion ("headache" in "i have a head ache")
            # Only do this for symptoms valid enough (len > 3) to avoid noise
            if len(norm_sym) > 3:
                collapsed_sym = norm_sym.replace(" ", "")
                if collapsed_sym in collapsed_query:
                     matched_symptoms.append(original_sym)
        
        if matched_symptoms:
            # Collect all unique Varma points for these symptoms
            target_varma_names = set()
            for sym in matched_symptoms:
                varma_list = self.symptom_map.get(sym, [])
                for v in varma_list:
                    target_varma_names.add(self.normalize(v))
            
            # Retrieve full details
            results = []
            for point in self.varma_db:
                if self.normalize(point.get("varmaName", "")) in target_varma_names:
                    results.append(point)
            
            return "symptom", results

        # 3. No match found
        return None, []
