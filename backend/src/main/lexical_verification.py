import re
from typing import Set

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
    suffixes = [
        'ness', 'iness', 'ing', 'ed', 'ly',
        'er', 'est', 'y', 'ity', 'ies', 's'
    ]

    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            root = word[:-len(suffix)]
            if suffix == 'iness' and not root.endswith('i'):
                root += 'y'
            return root

    return word

class LexicalVerifier:
    @staticmethod
    def extract_core_medical_terms(text: str) -> Set[str]:
        common_modifiers = {
            'loss', 'of', 'lack', 'absence', 'decrease',
            'increase', 'reduced', 'excessive', 'severe',
            'mild', 'chronic', 'acute', 'sudden', 'gradual', 'pain'
        }

        words = _normalize_text(text).split()
        core_terms: Set[str] = set()

        for word in words:
            if word not in common_modifiers and len(word) > 2:
                core_terms.add(word)

                root = _get_root_word(word)
                if root != word:
                    core_terms.add(root)

        return core_terms

    @staticmethod
    def verify(query: str, symptom: str) -> float:
        query_core = LexicalVerifier.extract_core_medical_terms(query)
        symptom_core = LexicalVerifier.extract_core_medical_terms(symptom)

        if not query_core or not symptom_core:
            return 0.0

        overlap = query_core.intersection(symptom_core)
        if not overlap:
            return 0.0

        precision = len(overlap) / len(query_core)
        recall = len(overlap) / len(symptom_core)

        return (2 * precision * recall) / (precision + recall)
