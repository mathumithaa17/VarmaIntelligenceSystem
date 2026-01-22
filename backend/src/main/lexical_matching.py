import re
from typing import List, Tuple, Set, Dict
from difflib import SequenceMatcher
from .medical_synonyms import MedicalSynonymDict

def _normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower().strip()
    s = re.sub(r'[\t\n\r]+', ' ', s)
    s = re.sub(r'[^\w\s\-]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def _get_root_word(word: str) -> str:
    word = word.lower().strip()
    suffixes = ['ness', 'iness', 'ing', 'ed', 'ly', 'er', 'est', 'y', 'ity', 'ies', 's']
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            root = word[:-len(suffix)]
            if suffix == 'iness' and not root.endswith('i'):
                root = root + 'y'
            return root
    return word

class LexicalMatcher:    
    def __init__(self, all_symptoms: List[str]):
        self.all_symptoms = all_symptoms
        self.all_symptoms_norm_to_orig = {_normalize_text(s): s for s in all_symptoms}
        
        # Initialize medical synonym dictionary
        self.synonym_dict = MedicalSynonymDict()
        
        self.word_to_symptoms: Dict[str, List[str]] = {}
        for symptom in all_symptoms:
            sym_norm = _normalize_text(symptom)
            words = sym_norm.split()
            for word in words:
                root = _get_root_word(word)
                self.word_to_symptoms.setdefault(root, []).append(symptom)
                
                # Also index by canonical form
                canonical = self.synonym_dict.get_canonical_form(word)
                if canonical != word:
                    self.word_to_symptoms.setdefault(canonical, []).append(symptom)
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from query
        IMPROVED: Only expands with synonyms for complete meaningful phrases
        """
        stop_words = {
            'i', 'am', 'have', 'having', 'feel', 'feeling', 'experience', 'experiencing',
            'my', 'the', 'a', 'an', 'and', 'or', 'but', 'with', 'from', 'there', 'is',
            'are', 'was', 'been', 'being', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'me', 'very', 'some',
            'severe', 'mild', 'slight', 'really', 'quite', 'just', 'also', 'serious',
            'recently', 'now', 'today', 'yesterday', 'since', 'for', 'last', 'two', 'days'
        }
        
        query_lower = query.lower().strip()
        
        # First normalize the query to handle phrases like "head pain" -> "headache"
        normalized_full_query = self.synonym_dict.normalize_medical_phrase(query_lower)
        
        all_phrases = [normalized_full_query]
        
        # Only expand if normalized query is a known medical term
        if normalized_full_query in self.synonym_dict.word_to_canonical:
            canonical = self.synonym_dict.word_to_canonical[normalized_full_query]
            synonyms = self.synonym_dict.synonym_groups.get(canonical, set())
            all_phrases.extend(list(synonyms))
        
        # Extract n-grams from the query
        words = query_lower.split()
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Add bigrams and trigrams
        for i in range(len(filtered_words)):
            # Single word - but ONLY if not context-dependent
            word = filtered_words[i]
            if not self.synonym_dict.is_context_dependent(word):
                all_phrases.append(word)
                root = _get_root_word(word)
                if root != word:
                    all_phrases.append(root)
            
            # Bigrams
            if i < len(filtered_words) - 1:
                bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
                all_phrases.append(bigram)
                
                # Normalize bigram
                normalized_bigram = self.synonym_dict.normalize_medical_phrase(bigram)
                if normalized_bigram != bigram:
                    all_phrases.append(normalized_bigram)
                    
                    # Add synonyms of normalized bigram
                    if normalized_bigram in self.synonym_dict.word_to_canonical:
                        canonical = self.synonym_dict.word_to_canonical[normalized_bigram]
                        synonyms = self.synonym_dict.synonym_groups.get(canonical, set())
                        all_phrases.extend(list(synonyms))
            
            # Trigrams
            if i < len(filtered_words) - 2:
                trigram = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
                all_phrases.append(trigram)
                
                # Normalize trigram
                normalized_trigram = self.synonym_dict.normalize_medical_phrase(trigram)
                if normalized_trigram != trigram:
                    all_phrases.append(normalized_trigram)
                    
                    # Add synonyms of normalized trigram
                    if normalized_trigram in self.synonym_dict.word_to_canonical:
                        canonical = self.synonym_dict.word_to_canonical[normalized_trigram]
                        synonyms = self.synonym_dict.synonym_groups.get(canonical, set())
                        all_phrases.extend(list(synonyms))
        
        # Remove duplicates
        return list(set(all_phrases))
    
    def calculate_word_similarity(self, word1: str, word2: str) -> float:
        # Check if they are synonyms
        if self.synonym_dict.are_synonyms(word1, word2):
            return 1.0
        
        # Check canonical forms
        canonical1 = self.synonym_dict.get_canonical_form(word1)
        canonical2 = self.synonym_dict.get_canonical_form(word2)
        if canonical1 == canonical2:
            return 1.0
        
        # Original similarity logic
        if len(word1) >= 3 and len(word2) >= 3:
            if word1 in word2 or word2 in word1:
                minl = min(len(word1), len(word2))
                maxl = max(len(word1), len(word2))
                coverage = minl / maxl
                if coverage >= 0.5:
                    return 0.90 * coverage
        
        ratio = SequenceMatcher(None, word1, word2).ratio()
        if ratio >= 0.60:
            return 0.85 * ratio
        
        return 0.0
    
    def _is_context_dependent_mismatch(self, query_term: str, symptom: str) -> bool:
        """
        CRITICAL: Check if we're trying to match a specific pain query to generic pain
        OR if body parts are completely mismatched
        Returns True if this is an invalid match that should be blocked
        """
        query_words = query_term.lower().split()
        symptom_words = symptom.lower().split()
        
        # Context-dependent words that need body parts
        pain_related = {'pain', 'ache', 'aching', 'sore', 'hurts', 'hurting', 'strain', 'swelling'}
        
        # Generic anatomical terms that should NOT be used for matching alone
        generic_terms = {'joint', 'limb', 'limbs', 'muscle', 'bone', 'tissue', 'region', 'area', 'extremities', 'body'}
        
        # Stop words to ignore
        stop_words = {'in', 'the', 'of', 'and', 'to', 'my', 'a', 'an', 'due', 'with', 'from', 'both', 'all'}
        
        # Anatomical regions and their strict related terms
        body_part_groups = {
            'head': {'head', 'cranial', 'skull', 'cephalalgia'},
            'face': {'face', 'facial', 'cheek'},
            'nose': {'nose', 'nasal'},
            'eye': {'eye', 'eyes', 'ocular'},
            'mouth': {'mouth', 'oral'},
            'teeth': {'teeth', 'tooth', 'dental'},
            'neck': {'neck', 'cervical', 'cervicalgia'},
            'shoulder': {'shoulder'},
            'arm': {'arm'},
            'elbow': {'elbow', 'forearm'},
            'wrist': {'wrist'},
            'hand': {'hand', 'hands', 'finger', 'fingers', 'palm', 'dorsum', 'thumb'},
            'chest': {'chest', 'thoracic', 'cardiac'},
            'abdomen': {'abdomen', 'abdominal', 'stomach', 'belly', 'gastric', 'tummy'},
            'back': {'back', 'spinal', 'vertebral', 'paravertebral'},
            'rectum': {'rectum', 'rectal', 'anus'},
            'hip': {'hip'},
            'leg': {'leg'},
            'knee': {'knee'},
            'ankle': {'ankle'},
            'foot': {'foot', 'toe', 'heel', 'calcaneal'},
        }
        
        # Special handling for "limb/limbs" - need context
        # "upper limbs" → arm region, "lower limbs" → leg region
        symptom_text = ' '.join(symptom_words)
        query_text = ' '.join(query_words)
        
        # Extract body parts from query and symptom
        query_body_parts = set()
        symptom_body_parts = set()
        
        # Handle "upper limbs" and "lower limbs" specially
        if 'upper' in symptom_text and ('limb' in symptom_text or 'limbs' in symptom_text):
            symptom_body_parts.add('arm')  # Treat "upper limbs" as arm region
        if 'lower' in symptom_text and ('limb' in symptom_text or 'limbs' in symptom_text):
            symptom_body_parts.add('leg')  # Treat "lower limbs" as leg region
        
        if 'upper' in query_text and ('limb' in query_text or 'limbs' in query_text):
            query_body_parts.add('arm')
        if 'lower' in query_text and ('limb' in query_text or 'limbs' in query_text):
            query_body_parts.add('leg')
        
        for word in query_words:
            if word not in pain_related and word not in generic_terms and word not in stop_words:
                for region, terms in body_part_groups.items():
                    if word in terms:
                        query_body_parts.add(region)
                        break
        
        for word in symptom_words:
            if word not in pain_related and word not in generic_terms and word not in stop_words:
                for region, terms in body_part_groups.items():
                    if word in terms:
                        symptom_body_parts.add(region)
                        break
        
        # CRITICAL CHECK: If both query and symptom mention specific body parts,
        # they MUST be the same or very closely related
        if query_body_parts and symptom_body_parts:
            # Check if they share any body part
            common_parts = query_body_parts.intersection(symptom_body_parts)
            if common_parts:
                return False  # Same body part - ALLOW
            
            # Special allowances for closely related parts ONLY
            # Elbow can match with arm ONLY if it says "upper"
            if 'elbow' in query_body_parts:
                if 'arm' in symptom_body_parts:
                    # Must explicitly say "upper" to match elbow
                    if 'upper' in ' '.join(symptom_words):
                        return False  # "elbow" can match "upper limbs/arm" - ALLOW
                    else:
                        return True  # "elbow" does NOT match generic "limbs" - BLOCK
            
            # Hand is close to elbow but not the same
            if 'elbow' in query_body_parts:
                if 'hand' in symptom_body_parts:
                    return True  # Different - BLOCK
            
            # Check for upper vs lower body mismatch
            upper_body = {'head', 'face', 'nose', 'eye', 'mouth', 'teeth', 'neck', 'shoulder', 'arm', 'elbow', 'wrist', 'hand', 'chest'}
            lower_body = {'hip', 'leg', 'knee', 'ankle', 'foot'}
            torso = {'abdomen', 'back', 'rectum'}
            
            query_is_upper = bool(query_body_parts & upper_body)
            query_is_lower = bool(query_body_parts & lower_body)
            query_is_torso = bool(query_body_parts & torso)
            symptom_is_upper = bool(symptom_body_parts & upper_body)
            symptom_is_lower = bool(symptom_body_parts & lower_body)
            symptom_is_torso = bool(symptom_body_parts & torso)
            
            # Strict separation: upper/lower/torso must match
            if query_is_upper and (symptom_is_lower or symptom_is_torso):
                return True
            if query_is_lower and (symptom_is_upper or symptom_is_torso):
                return True
            if query_is_torso and (symptom_is_upper or symptom_is_lower):
                return True
            
            # Otherwise, different body parts - BLOCK
            return True
        
        # If query has body parts but symptom doesn't, BLOCK
        if query_body_parts and not symptom_body_parts:
            return True
        
        # Pain-specific checks
        query_has_pain = any(word in pain_related for word in query_words)
        symptom_has_pain = any(word in pain_related for word in symptom_words)
        
        if len(query_words) > 1 and query_has_pain:
            if symptom_has_pain:
                # If symptom is ONLY a single generic pain word, BLOCK IT
                if len(symptom_words) == 1 and symptom_words[0] in pain_related:
                    return True  # INVALID MATCH - block it
                
                # Both have pain - check if body parts match
                if len(symptom_words) > 1:
                    # Get non-pain, non-generic words from both
                    query_specific = set(query_words) - pain_related - generic_terms - stop_words
                    symptom_specific = set(symptom_words) - pain_related - generic_terms - stop_words
                    
                    # STRICT: Must have exact body part match
                    exact_match = query_specific.intersection(symptom_specific)
                    if exact_match:
                        return False  # Exact match - ALLOW
                    
                    # Check if they're in the same region
                    if query_body_parts and symptom_body_parts:
                        if not query_body_parts.intersection(symptom_body_parts):
                            # Check for special allowances
                            if 'elbow' in query_body_parts and 'arm' in symptom_body_parts:
                                if 'upper' in ' '.join(symptom_words):
                                    return False  # Allow
                            return True  # Different regions - BLOCK
        
        return False  # Valid match
    
    def lexical_similarity(self, query_term: str, symptom: str) -> float:
        query_term = query_term.lower().strip()
        symptom = symptom.lower().strip()
        
        # CRITICAL: Block context-dependent mismatches FIRST
        if self._is_context_dependent_mismatch(query_term, symptom):
            return 0.0  # Return 0 score to completely block the match
        
        # Normalize both terms first
        normalized_query = self.synonym_dict.normalize_medical_phrase(query_term)
        normalized_symptom = self.synonym_dict.normalize_medical_phrase(symptom)
        
        # Check exact match
        if query_term == symptom:
            return 1.0
        
        # Check normalized match
        if normalized_query == normalized_symptom:
            return 0.99
        
        # Check synonym match
        if self.synonym_dict.are_synonyms(query_term, symptom):
            return 0.98
        
        if self.synonym_dict.are_synonyms(normalized_query, normalized_symptom):
            return 0.97
        
        # Check canonical forms
        canonical_query = self.synonym_dict.get_canonical_form(query_term)
        canonical_symptom = self.synonym_dict.get_canonical_form(symptom)
        if canonical_query == canonical_symptom:
            return 0.96
        
        # Special handling for "X pain" patterns
        if self._is_pain_related(query_term, symptom):
            return 0.95
        
        q_words = query_term.split()
        s_words = symptom.split()
        
        q_set = set(q_words)
        s_set = set(s_words)
        
        # Check if any words are synonyms
        for q_word in q_words:
            for s_word in s_words:
                if self.synonym_dict.are_synonyms(q_word, s_word):
                    return 0.92
        
        if q_set.issubset(s_set) and len(q_set) >= 2:
            return 0.95
        
        if len(q_words) == 1 and len(s_words) == 1:
            return self.calculate_word_similarity(q_words[0], s_words[0])
        
        best_scores = []
        for q in q_words:
            max_score = 0.0
            for s in s_words:
                score = self.calculate_word_similarity(q, s)
                max_score = max(max_score, score)
            if max_score > 0:
                best_scores.append(max_score)
        
        if best_scores:
            avg = sum(best_scores) / len(best_scores)
            coverage = len(best_scores) / max(len(q_words), len(s_words))
            return avg * (0.7 + 0.3 * coverage)
        
        if q_set.issubset(s_set):
            return 0.85 * (len(q_set) / len(s_set))
        
        inter = q_set.intersection(s_set)
        uni = q_set.union(s_set)
        if inter:
            jaccard = len(inter) / len(uni)
            if jaccard >= 0.5:
                return 0.80 * jaccard
        
        if query_term in symptom:
            return 0.75 * (len(query_term) / len(symptom))
        if symptom in query_term:
            return 0.75 * (len(symptom) / len(query_term))
        
        return 0.0
    
    def _is_pain_related(self, term1: str, term2: str) -> bool:
        """Check if two terms are pain-related and semantically similar"""
        pain_words = {'pain', 'ache', 'sore', 'discomfort', 'hurt'}
        
        # Extract non-pain words
        words1 = set(term1.split()) - pain_words
        words2 = set(term2.split()) - pain_words
        
        # If both have pain-related words and share body part
        has_pain1 = any(pw in term1 for pw in pain_words)
        has_pain2 = any(pw in term2 for pw in pain_words)
        
        if has_pain1 and has_pain2:
            # Check if they share body part words
            common_body_parts = words1.intersection(words2)
            if common_body_parts:
                return True
            
            # Check synonyms of body parts
            for w1 in words1:
                for w2 in words2:
                    if self.synonym_dict.are_synonyms(w1, w2):
                        return True
        
        return False
    
    def find_matches(self, query: str, threshold: float = 0.5) -> List[Tuple[str, float]]:
        qnorm = _normalize_text(query)
        keywords = self.extract_keywords(qnorm)
        
        candidate_symptoms = set()
        for keyword in keywords:
            kws = keyword.split()
            for w in kws:
                root = _get_root_word(w)
                if root in self.word_to_symptoms:
                    candidate_symptoms.update(self.word_to_symptoms[root])
                if w in self.word_to_symptoms:
                    candidate_symptoms.update(self.word_to_symptoms[w])
                
                # Check canonical form
                canonical = self.synonym_dict.get_canonical_form(w)
                if canonical in self.word_to_symptoms:
                    candidate_symptoms.update(self.word_to_symptoms[canonical])

        if not candidate_symptoms:
            candidate_symptoms = set(self.all_symptoms)
        
        matches = {}
        for symptom in candidate_symptoms:
            sym_norm = _normalize_text(symptom)
            max_score = 0.0
            
            # Check against normalized query
            score = self.lexical_similarity(qnorm, sym_norm)
            max_score = max(max_score, score)

            # Check against each keyword
            for keyword in keywords:
                score = self.lexical_similarity(keyword, sym_norm)
                max_score = max(max_score, score)
            
            if max_score >= threshold:
                matches[symptom] = max_score
        
        sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
        return sorted_matches