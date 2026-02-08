import json
from pathlib import Path
from typing import List, Dict, Any

class RuleBasedRetriever:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to the data directory relative to this file
            current_file = Path(__file__).resolve()
            data_dir = current_file.parent.parent / "data"
        
        self.data_dir = Path(data_dir)
        self.varma_db = []
        self.symptom_map = {}
        self.load_data()
    
    def load_data(self):
        """Load Varma data and symptom mapping from JSON files."""
        # Load varma_data.json
        varma_path = self.data_dir / "varma_data.json"
        with open(varma_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.varma_db = data.get("varmas", [])
        
        print(f"Loaded {len(self.varma_db)} Varma points from database")
        
        # Load symptom to varma mapping
        symptom_path = self.data_dir / "02_symptom_to_varma.json"
        with open(symptom_path, 'r', encoding='utf-8') as f:
            self.symptom_map = json.load(f)
        
        print(f"Loaded {len(self.symptom_map)} symptom mappings")
    
    def normalize(self, text: str) -> str:
        """
        Normalize text for matching: 
        1. Replace underscores with spaces
        2. Lowercase
        3. Strip whitespace
        4. Normalize internal whitespace (e.g. double spaces to single)
        """
        if not text:
            return ""
        
        # Replace underscore with space
        text = text.replace('_', ' ')
        
        # Lowercase and strip
        text = text.lower().strip()
        
        # Collapse multiple spaces
        return ' '.join(text.split())
    
    def fetch_varma_points(self, point_names: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch full JSON records for given Varma point names.
        Uses direct lookup with suffix fallback (Varmam <-> Kaalam).
        """
        results = []
        
        for point_name in point_names:
            # 1. Try original query
            match = self._find_point_in_db(point_name)
            
            # 2. If not found, try swapping suffixes
            if not match:
                variations = self._generate_suffix_variations(point_name)
                for var_name in variations:
                    match = self._find_point_in_db(var_name)
                    if match:
                        print(f"Found match using variation: '{var_name}'")
                        break
            
            if match:
                results.append(match)
        
        print(f"Fetched {len(results)} Varma points")
        return results

    def _find_point_in_db(self, query: str) -> Dict[str, Any]:
        """
        Helper to search for a single point name in DB using Hybrid Strategy.
        1. Exact Match (Best)
        2. Space-Insensitive Exact Match (e.g. "Vishamanibantha" == "Visha Manibantha")
        3. Longest Partial Match (Prefer "Visha Manibantha" over "Manibantha" if both present)
        """
        normalized_query = self.normalize(query)
        query_no_sapce = normalized_query.replace(" ", "")
        
        # Tier 1: Exact Match
        for point in self.varma_db:
            db_name = self.normalize(point.get("varmaName", ""))
            if normalized_query == db_name: 
                return point
        
        # Tier 2: Space-Insensitive Exact Match
        for point in self.varma_db:
            db_name = self.normalize(point.get("varmaName", ""))
            if query_no_sapce == db_name.replace(" ", ""):
                return point

        # Tier 3: Longest Partial Match
        # Collect all candidates where substring match occurs
        candidates = []
        for point in self.varma_db:
            db_name = self.normalize(point.get("varmaName", ""))
            
            # Check if query is in DB name OR DB name is in query
            if normalized_query in db_name or db_name in normalized_query:
                candidates.append((db_name, point))
        
        if candidates:
            # Sort by length of the DB name, descending
            # We want the longest matching term (most specific)
            # e.g. "Manibantha" (len 10) vs "Visha Manibantha" (len 16)
            # If query is "Visha Manibantha", both match, but we want the longer one.
            candidates.sort(key=lambda x: len(x[0]), reverse=True)
            best_match_name, best_match_point = candidates[0]
            return best_match_point
                
        return None

    def _generate_suffix_variations(self, name: str) -> List[str]:
        """Generate variations by swapping Varmam/Kaalam/Kalam."""
        lower_name = name.lower()
        variations = []
        
        # Define suffixes to swap
        suffixes = ['varmam', 'kaalam', 'kalam', 'varma', 'kala']
        
        found_suffix = None
        base_name = name
        
        for suffix in suffixes:
            if suffix in lower_name:
                found_suffix = suffix
                # Remove suffix to get base
                # This is a simple replace; might need regex for robustness but sufficient for now
                # We replace the LAST occurrence to avoid issues with names like "Kalam Varmam" (hypothetical)
                parts = name.rsplit(suffix, 1) if suffix in name else name.rsplit(suffix.capitalize(), 1)
                # Actually, simple replacement with regex is safer to handle case insensitivity
                import re
                base_name = re.sub(f'{suffix}$', '', name, flags=re.IGNORECASE).strip()
                break
        
        if not found_suffix:
            base_name = name.strip()
            
        # Generate alternatives
        # If input was "Udhira Varmam", base is "Udhira"
        # Try appending: Kaalam, Kalam
        # If input was "Udhira Kaalam", base is "Udhira"
        # Try appending: Varmam, Varma
        
        if 'varmam' in lower_name or 'varma' in lower_name:
            variations.append(f"{base_name} Kaalam")
            variations.append(f"{base_name} Kalam")
        elif 'kaalam' in lower_name or 'kalam' in lower_name or 'kala' in lower_name:
            variations.append(f"{base_name} Varmam")
            variations.append(f"{base_name} Varma")
        else:
            # If no suffix, try adding both
            variations.append(f"{base_name} Varmam")
            variations.append(f"{base_name} Kaalam")
            
        return variations
    
    def fetch_symptom_points(self, symptom: str) -> List[Dict[str, Any]]:
        """
        Fetch Varma points for a given symptom.
        Flow: symptom -> point names -> full JSON records
        """
        normalized_symptom = self.normalize(symptom)
        
        # Step 1: Find matching symptom in symptom_map
        point_names = []
        for symptom_key, points in self.symptom_map.items():
            normalized_key = self.normalize(symptom_key)
            
            # Check if symptom matches (exact or contains)
            if normalized_symptom == normalized_key or normalized_symptom in normalized_key or normalized_key in normalized_symptom:
                point_names.extend(points)
                print(f"Symptom '{symptom_key}' matched, found {len(points)} points")
        
        if not point_names:
            print(f"No points found for symptom: {symptom}")
            return []
        
        # Remove duplicates
        point_names = list(set(point_names))
        print(f"Total unique points for symptom: {len(point_names)}")
        
        # Step 2: Fetch full JSON for those points
        return self.fetch_varma_points(point_names)
    
    def fetch_data(self, terms: Any, intent: str) -> List[Dict[str, Any]]:
        """
        Main entry point for data fetching.
        
        Args:
            terms: List of point names (for VARMA_POINT) or symptom string (for SYMPTOM)
            intent: "VARMA_POINT" or "SYMPTOM"
        
        Returns:
            List of full JSON records from varma_data.json
        """
        if intent == "VARMA_POINT":
            # terms should be a list of point names
            if isinstance(terms, str):
                terms = [terms]
            return self.fetch_varma_points(terms)
        
        elif intent == "SYMPTOM":
            # terms should be a symptom string
            if isinstance(terms, list):
                terms = terms[0] if terms else ""
            return self.fetch_symptom_points(terms)
        
        else:
            return []
