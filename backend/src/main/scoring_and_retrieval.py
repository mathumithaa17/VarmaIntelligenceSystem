import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
from .lexical_matching import LexicalMatcher, _normalize_text
from .semantic_matching import SemanticMatcher
from .lexical_verification import LexicalVerifier

class VarmaRetriever:
    def __init__(self, varma_symptoms_path: Path, symptom_to_varma_path: Path):
        print(f"Loading Varma data from:")
        print(f"  varma_symptoms: {varma_symptoms_path}")
        print(f"  symptom_to_varma: {symptom_to_varma_path}")
        
        with open(varma_symptoms_path, 'r', encoding='utf-8') as f:
            self.varma_data = json.load(f)
        
        with open(symptom_to_varma_path, 'r', encoding='utf-8') as f:
            self.symptom_to_varma = json.load(f)
        
        self.symptom_to_varma_norm: Dict[str, List[str]] = {}
        if isinstance(self.symptom_to_varma, dict):
            for k, v in self.symptom_to_varma.items():
                nk = _normalize_text(k)
                norm_ids = []
                if isinstance(v, list):
                    for item in v:
                        norm_ids.append(_normalize_text(str(item)))
                elif isinstance(v, str):
                    parts = re.split(r'[;,]', v)
                    for p in parts:
                        if p.strip():
                            norm_ids.append(_normalize_text(p.strip()))
                self.symptom_to_varma_norm[nk] = norm_ids
        
        self.varma_id_to_record: Dict[str, Dict] = {}
        if isinstance(self.varma_data, dict):
            for varma_name, symptoms in self.varma_data.items():
                nvid = _normalize_text(varma_name)
                self.varma_id_to_record[nvid] = {
                    "varma_name": varma_name,
                    "symptoms": symptoms
                }
        
        if isinstance(self.symptom_to_varma, dict):
            self.all_symptoms = list(self.symptom_to_varma.keys())
        else:
            self.all_symptoms = []
        
        print(f"Loaded {len(self.all_symptoms)} symptoms and {len(self.varma_data)} varma records")
        
        print("\nInitializing matchers...")
        self.lexical_matcher = LexicalMatcher(self.all_symptoms)
        self.semantic_matcher = SemanticMatcher(self.all_symptoms)
        self.lexical_verifier = LexicalVerifier()
        print("Initialization complete\n")
    
    def find_matching_symptoms(
        self,
        query: str,
        top_k: int = 15,
        lexical_threshold: float = 0.45,
        semantic_threshold: float = 0.55,
        verification_threshold: float = 0.3
    ) -> List[Tuple[str, float, str]]:
        
        print("\n[Stage 1] Lexical Matching...")
        lexical_matches = self.lexical_matcher.find_matches(query, lexical_threshold)
        
        high_confidence_lexical = [(s, sc) for s, sc in lexical_matches if sc >= 0.8]
        low_confidence_lexical = [(s, sc) for s, sc in lexical_matches if sc < 0.8]
        
        print(f"  Found {len(high_confidence_lexical)} high-confidence matches")
        print(f"  Found {len(low_confidence_lexical)} low-confidence matches")
        
        verified_semantic = []
        
        if self.semantic_matcher.semantic_available and len(high_confidence_lexical) < top_k:
            print("\n[Stage 2] Semantic Candidate Expansion...")
            semantic_matches = self.semantic_matcher.find_matches(
                query,
                top_k=top_k * 3,
                threshold=semantic_threshold
            )
            print(f"  → Found {len(semantic_matches)} semantic candidates")
            
            print("\n[Stage 3] Lexical Verification...")
            for symptom, sem_score in semantic_matches:
                if symptom in dict(high_confidence_lexical):
                    continue
                
                verification_score = self.lexical_verifier.verify(query, symptom)
                
                if verification_score >= verification_threshold:
                    verified_semantic.append((symptom, sem_score, verification_score))
                    print(f"  VERIFIED: {symptom[:40]} (sem={sem_score:.3f}, verify={verification_score:.3f})")
                else:
                    print(f"  REJECTED: {symptom[:40]} (sem={sem_score:.3f}, verify={verification_score:.3f})")
        
        final_results = {}
        match_types = {}
        
        for s, sc in high_confidence_lexical:
            final_results[s] = sc * 1.0
            match_types[s] = 'lexical-exact'
        
        for s, sem_sc, ver_sc in verified_semantic:
            if s not in final_results:
                final_results[s] = sem_sc * 0.6 + ver_sc * 0.4
                match_types[s] = 'semantic-verified'
        
        for s, sc in low_confidence_lexical:
            if s not in final_results:
                final_results[s] = sc * 0.7
                match_types[s] = 'lexical-partial'
        
        sorted_matches = sorted(final_results.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = [(symptom, score, match_types[symptom]) for symptom, score in sorted_matches]
        
        print(f"\n[Final] Returning {len(results)} matches")
        return results
    
    def get_varma_points(
        self,
        symptoms_with_scores: List[Tuple[str, float, str]],
        num_query_symptoms: int
    ) -> Dict[str, Dict]:
        
        varma_scores: Dict[str, Dict] = {}
        
        for symptom, score, match_type in symptoms_with_scores:
            norm_sym = _normalize_text(symptom)
            varma_ids = self.symptom_to_varma_norm.get(norm_sym)
            
            if not varma_ids:
                best_key = None
                best_ratio = 0.0
                for candidate in self.symptom_to_varma_norm.keys():
                    r = SequenceMatcher(None, norm_sym, candidate).ratio()
                    if r > best_ratio:
                        best_ratio = r
                        best_key = candidate
                if best_ratio >= 0.85 and best_key:
                    varma_ids = self.symptom_to_varma_norm.get(best_key)
            
            if not varma_ids:
                continue
            
            for vid in varma_ids:
                if vid not in varma_scores:
                    varma_scores[vid] = {
                        'count': 0,
                        'matched_symptoms': [],
                        'total_score': 0.0,
                        'exact_count': 0,
                        'verified_count': 0,
                        'partial_count': 0,
                        'weighted_score': 0.0,
                        'symptom_scores': []
                    }
                
                entry = varma_scores[vid]
                entry['count'] += 1
                entry['matched_symptoms'].append(symptom)
                entry['total_score'] += score
                entry['symptom_scores'].append(score)
                
                if match_type == 'lexical-exact':
                    entry['exact_count'] += 1
                    entry['weighted_score'] += score * 10.0
                elif match_type == 'semantic-verified':
                    entry['verified_count'] += 1
                    entry['weighted_score'] += score * 5.0
                else:
                    entry['partial_count'] += 1
                    entry['weighted_score'] += score * 2.0

        for vid, info in varma_scores.items():
            if info['count'] > 1:
                diversity_bonus = min(info['count'] / max(num_query_symptoms, 1), 1.0) * 3.0
                info['weighted_score'] += diversity_bonus
            
            avg_score = info['total_score'] / max(info['count'], 1)
            info['avg_match_quality'] = avg_score

            if info['exact_count'] > 1:
                info['weighted_score'] *= 1.3

        results: Dict[str, Dict] = {}
        for vid, info in varma_scores.items():
            rec = self.varma_id_to_record.get(vid)

            if not rec:
                best_id = None
                best_r = 0.0
                for cand in self.varma_id_to_record.keys():
                    r = SequenceMatcher(None, vid, cand).ratio()
                    if r > best_r:
                        best_r = r
                        best_id = cand
                if best_r >= 0.90 and best_id:
                    rec = self.varma_id_to_record.get(best_id)
            
            if not rec:
                name = vid
                symptoms_list = []
            else:
                name = rec.get('varma_name') or rec.get('varmaName') or rec.get('name') or vid
                symptoms_list = rec.get('symptoms') or rec.get('signs') or []
            
            results[vid] = {
                'varma_name': name,
                'matched_symptom_count': info['count'],
                'matched_symptoms': info['matched_symptoms'],
                'total_symptoms': len(symptoms_list),
                'all_symptoms': symptoms_list,
                'total_score': info['total_score'],
                'weighted_score': info['weighted_score'],
                'exact_count': info['exact_count'],
                'verified_count': info['verified_count'],
                'partial_count': info['partial_count'],
                'avg_match_quality': info.get('avg_match_quality', 0.0)
            }
        
        return results
    
    def retrieve(
        self,
        query: str,
        top_symptoms: int = 15,
        top_varmas: int = 5,
        lexical_threshold: float = 0.45,
        semantic_threshold: float = 0.55,
        verification_threshold: float = 0.3
    ) -> Dict:
        
        print(f"\n{'='*80}")
        print(f"Analyzing query: '{query}'")
        print(f"{'='*80}")

        keywords = self.lexical_matcher.extract_keywords(query)
        num_query_symptoms = max(len([k for k in keywords if len(k.split()) == 1 and len(k) > 2]), 1)

        matched_symptoms = self.find_matching_symptoms(
            query,
            top_k=top_symptoms,
            lexical_threshold=lexical_threshold,
            semantic_threshold=semantic_threshold,
            verification_threshold=verification_threshold
        )
        
        if not matched_symptoms:
            return {
                'query': query,
                'matched_symptoms': [],
                'varma_points': [],
                'message': 'No matching symptoms found. Try rephrasing your query.'
            }

        print(f"\n{'='*80}")
        print(f"Top {len(matched_symptoms)} Matching Symptoms:")
        print(f"{'-'*80}")
        for symptom, score, match_type in matched_symptoms:
            print(f"{symptom:<45} (score: {score:.3f}, {match_type})")

        varma_results = self.get_varma_points(matched_symptoms, num_query_symptoms)

        ranked = sorted(
            varma_results.items(),
            key=lambda x: (
                x[1]['exact_count'],
                x[1]['matched_symptom_count'],
                x[1]['weighted_score'],
                x[1].get('avg_match_quality', 0.0)
            ),
            reverse=True
        )[:top_varmas]
        
        varma_list = []
        for vid, info in ranked:
            total_symptoms = info.get('total_symptoms') or 0
            match_percentage = round(100 * info['matched_symptom_count'] / total_symptoms, 2) if total_symptoms else 0.0
            varma_list.append({
                'varma_id': vid,
                'varma_name': info['varma_name'],
                'matched_symptom_count': info['matched_symptom_count'],
                'total_symptoms': total_symptoms,
                'match_percentage': match_percentage,
                'matched_symptoms': info['matched_symptoms'],
                'all_symptoms': info['all_symptoms'],
                'weighted_score': info['weighted_score'],
                'exact_count': info['exact_count'],
                'verified_count': info['verified_count'],
                'partial_count': info['partial_count'],
                'avg_match_quality': info.get('avg_match_quality', 0.0)
            })

        print(f"\n{'='*80}")
        print(f"Top {len(varma_list)} Varma Points:")
        print(f"{'='*80}")
        for i, varma in enumerate(varma_list, 1):
            confidence = "HIGH" if varma['exact_count'] > 0 else "MEDIUM"
            print(f"\n{i}. {varma['varma_name']} (ID: {varma['varma_id']}) [{confidence}]")
            print(f"   Matched: {varma['matched_symptom_count']}/{varma['total_symptoms']} ({varma['match_percentage']}%)")
            print(f"   Exact: {varma['exact_count']}, Verified: {varma['verified_count']}, Partial: {varma['partial_count']}")
            print(f"   Confidence Score: {varma['weighted_score']:.2f} | Avg Quality: {varma['avg_match_quality']:.2f}")
            print(f"   Symptoms: {', '.join(varma['matched_symptoms'][:5])}")
            if len(varma['matched_symptoms']) > 5:
                print(f"           ... and {len(varma['matched_symptoms']) - 5} more")
        
        return {
            'query': query,
            'matched_symptoms': [
                {'symptom': s, 'combined_score': score, 'match_type': mtype}
                for s, score, mtype in matched_symptoms
            ],
            'varma_points': varma_list
        }

def compute_confidence(weighted_score: float = None, top_symptom_score: float = None, scale: float = 5.0) -> float:
    try:
        if weighted_score is not None and weighted_score > 0:
            w = float(weighted_score)
            return float(w / (w + scale))
        if top_symptom_score is not None and top_symptom_score > 0:
            s = float(top_symptom_score)
            return float(s / (s + 1.0))
    except Exception:
        pass
    return 0.0
