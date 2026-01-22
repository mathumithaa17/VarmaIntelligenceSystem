import numpy as np
from typing import List, Tuple, Optional

semantic_available = True
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
except Exception:
    print("WARNING: transformers/torch not available. Semantic matching disabled.")
    AutoTokenizer = None
    AutoModel = None
    torch = None
    semantic_available = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    print("WARNING: sklearn not available. Semantic matching disabled.")
    cosine_similarity = None
    semantic_available = False

class SemanticMatcher:
    def __init__(self, all_symptoms: List[str]):
        self.all_symptoms = all_symptoms
        self.semantic_available = semantic_available
        self.tokenizer = None
        self.model = None
        self.symptom_embeddings = None
        
        if self.semantic_available:
            try:
                print("Loading PubMedBERT model...")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
                )
                self.model = AutoModel.from_pretrained(
                    "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
                )
                if self.model is not None and torch is not None:
                    self.model.eval()
                print("✓ PubMedBERT loaded successfully")
                
                print("Computing symptom embeddings...")
                self.symptom_embeddings = self._compute_embeddings(all_symptoms)
                print(f"Computed embeddings for {len(all_symptoms)} symptoms")
                
            except Exception as e:
                print(f"WARNING: Could not load PubMedBERT - {e}")
                self.semantic_available = False
                self.tokenizer = None
                self.model = None
        else:
            print("Semantic matching disabled (missing dependencies)")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        if not self.semantic_available or self.tokenizer is None or self.model is None:
            raise RuntimeError("Semantic model not available")
        
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)

        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()[0]
    
    def _compute_embeddings(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for i, text in enumerate(texts):
            if (i + 1) % 50 == 0:
                print(f"  Embedding {i+1}/{len(texts)}")
            embeddings.append(self._get_embedding(text))
        return np.array(embeddings)
    
    def find_matches(self, query: str, top_k: int = 20, threshold: float = 0.55) -> List[Tuple[str, float]]:
        if not self.semantic_available or self.symptom_embeddings is None or cosine_similarity is None:
            return []
        
        try:
            q_emb = self._get_embedding(query).reshape(1, -1)
            sims = cosine_similarity(q_emb, self.symptom_embeddings)[0]
            top_idx = np.argsort(sims)[::-1][:top_k]
            matches = [
                (self.all_symptoms[i], float(sims[i]))
                for i in top_idx
                if sims[i] >= threshold
            ]
            
            return matches
        
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return []