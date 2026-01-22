"""
Medical Synonym Dictionary for Varma System
Maps medical terms to their synonyms and related terms
Enhanced with context-aware matching to prevent overly broad matches
"""

from typing import Set, List, Dict, Tuple
import re

class MedicalSynonymDict:
    """Comprehensive medical synonym dictionary for symptom matching"""
    
    def __init__(self):
        # Core medical synonyms - organized by category
        self.synonym_groups = {
            # Consciousness-related
            'unconscious': {'unconscious', 'unconsciousness', 'loss of consciousness', 
                          'unresponsive', 'syncope', 'fainting', 'faint', 'passed out',
                          'blackout', 'insensible'},
            
            # Dizziness-related
            'dizzy': {'dizzy', 'dizziness', 'vertigo', 'lightheaded', 'light headed',
                     'giddy', 'giddiness', 'spinning sensation', 'wooziness', 'woozy',
                     'unsteady', 'off balance'},
            
            # Headache-related - ENHANCED
            'headache': {'headache', 'head ache', 'cephalalgia', 'head pain',
                        'migraine', 'cranial pain', 'skull pain', 'pain in head',
                        'pain in the head', 'ache in head', 'pain head',
                        'head hurts', 'pain at head'},
            
            # Pain locations - SPECIFIC (removed generic "pain")
            'neck pain': {'neck pain', 'cervicalgia', 'pain in neck', 'stiff neck',
                         'neck ache', 'sore neck', 'pain in the neck', 'neck hurts'},
            'shoulder pain': {'shoulder pain', 'pain in shoulder', 'shoulder ache',
                            'pain in the shoulder', 'shoulder hurts'},
            'back pain': {'back pain', 'backache', 'pain in back', 'spinal pain',
                         'pain in the back', 'back hurts'},
            'chest pain': {'chest pain', 'chest discomfort', 'angina',
                          'cardiac pain', 'thoracic pain', 'pain in chest',
                          'pain in the chest', 'chest hurts'},
            'abdomen pain': {'abdomen pain', 'abdominal pain', 'stomach pain',
                            'belly pain', 'tummy pain', 'gastric pain',
                            'pain in abdomen', 'pain in stomach', 'stomach ache',
                            'pain in the abdomen', 'pain in the stomach'},
            'joint pain': {'joint pain', 'arthralgia', 'joint ache', 'polyarthralgia',
                          'pain in joints', 'pain in the joints'},
            'ear pain': {'ear pain', 'otalgia', 'earache', 'pain in ear',
                        'pain in the ear', 'ear hurts'},
            'eye pain': {'eye pain', 'ophthalmalgia', 'pain in eye', 'eye ache',
                        'pain in the eye', 'eye hurts'},
            'throat pain': {'throat pain', 'sore throat', 'pain in throat',
                           'pain in the throat', 'throat hurts'},
            'tooth pain': {'tooth pain', 'toothache', 'dental pain', 'pain in tooth',
                          'pain in the tooth', 'tooth hurts'},
            'arm pain': {'arm pain', 'pain in arm', 'pain in the arm', 'arm hurts'},
            'leg pain': {'leg pain', 'pain in leg', 'pain in the leg', 'leg hurts'},
            'hand pain': {'hand pain', 'pain in hand', 'pain in the hand', 'hand hurts'},
            'foot pain': {'foot pain', 'pain in foot', 'pain in the foot', 'foot hurts'},
            'elbow pain': {'elbow pain', 'pain in elbow', 'pain in the elbow', 'elbow hurts'},
            'knee pain': {'knee pain', 'pain in knee', 'pain in the knee', 'knee hurts'},
            'wrist pain': {'wrist pain', 'pain in wrist', 'pain in the wrist', 'wrist hurts'},
            'ankle pain': {'ankle pain', 'pain in ankle', 'pain in the ankle', 'ankle hurts'},
            
            # Nausea/Vomiting
            'nausea': {'nausea', 'nauseated', 'nauseous', 'sick to stomach',
                      'queasy', 'queasiness', 'feeling sick'},
            'vomiting': {'vomiting', 'vomit', 'emesis', 'throwing up', 'puking',
                        'hyperemesis', 'regurgitation'},
            
            # Severe pain (as distinct concept)
            'severe pain': {'severe pain', 'intense pain', 'excruciating pain',
                           'unbearable pain', 'agonizing pain', 'sharp pain',
                           'acute pain'},
            
            # Breathing-related
            'breathless': {'breathless', 'breathlessness', 'shortness of breath',
                          'dyspnoea', 'dyspnea', 'difficulty breathing', 'gasping',
                          'labored breathing', 'cant breathe', 'wheezing'},
            
            # Weakness-related
            'weakness': {'weakness', 'weak', 'debility', 'fatigue', 'tired',
                        'tiredness', 'exhaustion', 'lethargy', 'malaise',
                        'general weakness', 'body weakness'},
            'fatigue': {'fatigue', 'tired', 'tiredness', 'exhaustion', 'weariness',
                       'lethargy', 'lassitude', 'prostration'},
            
            # Fever-related
            'fever': {'fever', 'pyrexia', 'febrile', 'high temperature',
                     'temperature', 'hot', 'feverish', 'hyperthermia'},
            'chills': {'chills', 'chillness', 'shivering', 'shiver', 'rigor',
                      'cold', 'coldness', 'hypothermia', 'frigidity'},
            
            # Swelling-related
            'swelling': {'swelling', 'swollen', 'edema', 'oedema', 'inflammation',
                        'puffiness', 'bloating', 'distension', 'enlarged'},
            
            # Vision-related
            'blurred vision': {'blurred vision', 'blurry vision', 'visual impairment',
                              'reduced vision', 'diminished vision', 'poor vision',
                              'cloudy vision', 'hazy vision', 'vision loss'},
            'blindness': {'blindness', 'blind', 'vision loss', 'loss of vision',
                         'cannot see', 'unable to see'},
            
            # Hearing-related
            'deafness': {'deafness', 'deaf', 'hearing loss', 'loss of hearing',
                        'hearing impairment', 'cannot hear', 'unable to hear'},
            'tinnitus': {'tinnitus', 'ringing in ears', 'ear ringing', 'buzzing in ears'},
            
            # Seizure-related
            'seizure': {'seizure', 'seizures', 'convulsion', 'convulsions', 'fit',
                       'epilepsy', 'epileptic attack', 'spasm', 'status epilepticus'},
            
            # Tremor-related
            'tremor': {'tremor', 'tremors', 'shaking', 'trembling', 'quivering',
                      'twitching', 'shivering'},
            
            # Paralysis-related
            'paralysis': {'paralysis', 'paralyzed', 'unable to move', 'cant move',
                         'loss of movement', 'paraplegia', 'quadriplegia',
                         'hemiplegia', 'immobile'},
            
            # Numbness-related
            'numbness': {'numbness', 'numb', 'tingling', 'pins and needles',
                        'paraesthesia', 'paresthesia', 'loss of sensation'},
            
            # Abdominal issues
            'constipation': {'constipation', 'constipated', 'difficulty passing stool',
                            'hard stool', 'cant pass stool'},
            'diarrhea': {'diarrhea', 'diarrhoea', 'loose stool', 'watery stool',
                        'frequent stool', 'bowel movement'},
            
            # Urinary issues
            'urinary retention': {'urinary retention', 'unable to urinate',
                                 'cant urinate', 'cant pass urine',
                                 'difficulty urinating', 'retention of urine'},
            'frequent urination': {'frequent urination', 'polyuria', 'urinary frequency',
                                  'frequent passing urine'},
            
            # Speech-related
            'speech difficulty': {'speech difficulty', 'slurred speech', 'dysarthria',
                                 'cant speak', 'unable to speak', 'aphasia',
                                 'difficulty speaking'},
            
            # Breathing sounds
            'wheezing': {'wheezing', 'wheeze', 'whistling breath', 'noisy breathing'},
            'cough': {'cough', 'coughing', 'productive cough', 'dry cough'},
            
            # Mental status
            'confusion': {'confusion', 'confused', 'disoriented', 'disorientation',
                         'delirium', 'mental confusion', 'altered mental state'},
            'anxiety': {'anxiety', 'anxious', 'nervous', 'nervousness', 'worried',
                       'panic', 'fear', 'fearfulness'},
            
            # Skin-related
            'redness': {'redness', 'red', 'erythema', 'flushing', 'inflammation'},
            'paleness': {'paleness', 'pale', 'pallor', 'white', 'colorless'},
            'cyanosis': {'cyanosis', 'blue', 'bluish', 'blue discoloration',
                        'bluish discoloration'},
            
            # Joint/Movement
            'stiffness': {'stiffness', 'stiff', 'rigidity', 'rigid', 'inflexible'},
            
            # Chest-related
            'palpitation': {'palpitation', 'palpitations', 'rapid heartbeat',
                           'fast heartbeat', 'irregular heartbeat', 'heart racing'},
        }
        
        # IMPORTANT: Words that should NOT be expanded on their own
        # These words should only match when part of a specific phrase
        self.context_dependent_words = {
            'pain', 'ache', 'aching', 'sore', 'soreness', 'discomfort',
            'tenderness', 'hurting', 'painful', 'hurts'
        }
        
        # Build reverse lookup: word -> canonical term
        self.word_to_canonical = {}
        for canonical, synonyms in self.synonym_groups.items():
            for syn in synonyms:
                self.word_to_canonical[syn.lower()] = canonical
        
        # Medical prefixes and suffixes for stemming
        self.medical_prefixes = {
            'hyper': 'excessive',
            'hypo': 'reduced',
            'a': 'without',
            'an': 'without',
            'dys': 'difficult',
            'poly': 'many',
            'oligo': 'few',
            'tachy': 'fast',
            'brady': 'slow',
        }
        
        self.medical_suffixes = {
            'algia': 'pain',
            'itis': 'inflammation',
            'osis': 'condition',
            'emia': 'blood condition',
            'pathy': 'disease',
            'penia': 'deficiency',
            'ectomy': 'removal',
        }
    
    def normalize_medical_phrase(self, phrase: str) -> str:
        """
        Normalize medical phrases to standard form
        Handles patterns like "head pain" -> "headache"
        """
        phrase = phrase.lower().strip()
        
        # Direct phrase mappings
        phrase_map = {
            'head pain': 'headache',
            'pain in head': 'headache',
            'pain in the head': 'headache',
            'pain head': 'headache',
            'ache in head': 'headache',
            'head ache': 'headache',
            'head hurts': 'headache',
            'pain at head': 'headache',
            
            'stomach pain': 'abdomen pain',
            'belly pain': 'abdomen pain',
            'tummy pain': 'abdomen pain',
            'pain in stomach': 'abdomen pain',
            'pain in abdomen': 'abdomen pain',
            'pain in the stomach': 'abdomen pain',
            'pain in the abdomen': 'abdomen pain',
            'stomach ache': 'abdomen pain',
            
            'ear pain': 'otalgia',
            'pain in ear': 'otalgia',
            'earache': 'otalgia',
            'pain in the ear': 'otalgia',
            'ear hurts': 'otalgia',
            
            'eye pain': 'ophthalmalgia',
            'pain in eye': 'ophthalmalgia',
            'pain in the eye': 'ophthalmalgia',
            'eye hurts': 'ophthalmalgia',
            
            'neck pain': 'cervicalgia',
            'pain in neck': 'cervicalgia',
            'pain in the neck': 'cervicalgia',
            'neck hurts': 'cervicalgia',
            
            'chest pain': 'chest pain',
            'pain in chest': 'chest pain',
            'pain in the chest': 'chest pain',
            'chest hurts': 'chest pain',
            
            'back pain': 'back pain',
            'pain in back': 'back pain',
            'pain in the back': 'back pain',
            'back hurts': 'back pain',
            
            'joint pain': 'arthralgia',
            'pain in joints': 'arthralgia',
            'pain in the joints': 'arthralgia',
            
            'throat pain': 'sore throat',
            'pain in throat': 'sore throat',
            'pain in the throat': 'sore throat',
            'throat hurts': 'sore throat',
            
            # Additional body parts
            'arm pain': 'arm pain',
            'pain in arm': 'arm pain',
            'pain in the arm': 'arm pain',
            
            'leg pain': 'leg pain',
            'pain in leg': 'leg pain',
            'pain in the leg': 'leg pain',
            
            'hand pain': 'hand pain',
            'pain in hand': 'hand pain',
            'pain in the hand': 'hand pain',
            
            'foot pain': 'foot pain',
            'pain in foot': 'foot pain',
            'pain in the foot': 'foot pain',
            
            'elbow pain': 'elbow pain',
            'pain in elbow': 'elbow pain',
            'pain in the elbow': 'elbow pain',
            
            'knee pain': 'knee pain',
            'pain in knee': 'knee pain',
            'pain in the knee': 'knee pain',
            
            'wrist pain': 'wrist pain',
            'pain in wrist': 'wrist pain',
            'pain in the wrist': 'wrist pain',
            
            'ankle pain': 'ankle pain',
            'pain in ankle': 'ankle pain',
            'pain in the ankle': 'ankle pain',
            
            'shoulder pain': 'shoulder pain',
            'pain in shoulder': 'shoulder pain',
            'pain in the shoulder': 'shoulder pain',
            
            # Breathing patterns
            'cant breathe': 'dyspnoea',
            'cannot breathe': 'dyspnoea',
            'difficulty breathing': 'dyspnoea',
            'hard to breathe': 'dyspnoea',
            'trouble breathing': 'dyspnoea',
            
            # Consciousness patterns
            'loss of consciousness': 'unconscious',
            'passed out': 'unconscious',
            'blacked out': 'unconscious',
            
            # Vision patterns
            'cant see': 'blindness',
            'cannot see': 'blindness',
            'loss of vision': 'blindness',
            
            # Hearing patterns
            'cant hear': 'deafness',
            'cannot hear': 'deafness',
            'loss of hearing': 'deafness',
            
            # Movement patterns
            'cant move': 'paralysis',
            'cannot move': 'paralysis',
            'unable to move': 'paralysis',
        }
        
        # Check exact phrase match first
        if phrase in phrase_map:
            return phrase_map[phrase]
        
        # Check for pattern: "[body_part] pain" or "[body_part] hurts"
        pain_pattern = re.match(r'(\w+)\s+(pain|ache|hurts)', phrase)
        if pain_pattern:
            body_part = pain_pattern.group(1)
            pain_word = pain_pattern.group(2)
            # Try to find mapped version
            for key in phrase_map:
                if body_part in key and (pain_word in key or 'pain' in key or 'ache' in key):
                    return phrase_map[key]
        
        # Check for pattern: "pain in [the] [body_part]"
        pain_in_pattern = re.match(r'pain\s+in\s+(?:the\s+)?(\w+)', phrase)
        if pain_in_pattern:
            body_part = pain_in_pattern.group(1)
            # Try to find mapped version
            for key in phrase_map:
                if f'pain in {body_part}' in key or f'pain in the {body_part}' in key:
                    return phrase_map[key]
        
        return phrase
    
    def get_canonical_form(self, term: str) -> str:
        """Get the canonical form of a medical term"""
        term = term.lower().strip()
        
        # First normalize the phrase
        normalized = self.normalize_medical_phrase(term)
        
        # Then check synonym dictionary
        return self.word_to_canonical.get(normalized, normalized)
    
    def are_synonyms(self, term1: str, term2: str) -> bool:
        """Check if two terms are synonyms"""
        canonical1 = self.get_canonical_form(term1.lower())
        canonical2 = self.get_canonical_form(term2.lower())
        return canonical1 == canonical2
    
    def get_all_synonyms(self, term: str) -> Set[str]:
        """Get all synonyms for a given term"""
        canonical = self.get_canonical_form(term.lower())
        return self.synonym_groups.get(canonical, {term.lower()})
    
    def is_context_dependent(self, word: str) -> bool:
        """Check if a word should only be matched in context"""
        return word.lower() in self.context_dependent_words
    
    def expand_query_with_synonyms(self, query: str) -> List[str]:
        """
        Expand a query with all possible synonyms
        IMPROVED: Prevents standalone expansion of context-dependent words like 'pain'
        """
        expanded = [query]
        query_lower = query.lower().strip()
        
        # First normalize the ENTIRE query phrase
        normalized_query = self.normalize_medical_phrase(query_lower)
        if normalized_query != query_lower:
            expanded.append(normalized_query)
            # If normalized, also get its synonyms
            if normalized_query in self.word_to_canonical:
                canonical = self.word_to_canonical[normalized_query]
                synonyms = self.synonym_groups.get(canonical, set())
                expanded.extend(list(synonyms))
        
        # Check for multi-word phrases in the original query
        for canonical, synonyms in self.synonym_groups.items():
            for syn in synonyms:
                if syn in query_lower:
                    # Add all other synonyms
                    for other_syn in synonyms:
                        if other_syn != syn:
                            new_query = query_lower.replace(syn, other_syn)
                            expanded.append(new_query)
        
        # Check for multi-word phrases in normalized query
        for canonical, synonyms in self.synonym_groups.items():
            for syn in synonyms:
                if syn in normalized_query:
                    for other_syn in synonyms:
                        if other_syn != syn:
                            new_query = normalized_query.replace(syn, other_syn)
                            expanded.append(new_query)
        
        # Check individual words ONLY if they're not context-dependent
        # OR if the query is just that single word
        words = query_lower.split()
        
        # Only expand individual words if:
        # 1. The query is a single word, OR
        # 2. The word is NOT context-dependent
        for word in words:
            # Skip context-dependent words unless query is just that word
            if self.is_context_dependent(word) and len(words) > 1:
                continue
            
            # Normalize individual words
            normalized_word = self.normalize_medical_phrase(word)
            if normalized_word != word:
                expanded.append(query_lower.replace(word, normalized_word))
            
            if word in self.word_to_canonical:
                synonyms = self.get_all_synonyms(word)
                for syn in synonyms:
                    if syn != word:
                        expanded.append(query_lower.replace(word, syn))
            
            if normalized_word in self.word_to_canonical:
                synonyms = self.get_all_synonyms(normalized_word)
                for syn in synonyms:
                    if syn != normalized_word:
                        expanded.append(query_lower.replace(word, syn))
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for item in expanded:
            if item not in seen:
                seen.add(item)
                result.append(item)
        
        return result