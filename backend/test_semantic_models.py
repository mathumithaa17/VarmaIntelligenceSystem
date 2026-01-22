import numpy as np
from typing import List, Tuple
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import time

class ModelTester:
    def __init__(self, model_name: str):
        self.model_name = model_name
        print(f"\n{'='*80}")
        print(f"Loading model: {model_name}")
        print(f"{'='*80}")
        
        try:
            start = time.time()
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.eval()
            elapsed = time.time() - start
            print(f"✓ Model loaded in {elapsed:.2f}s")
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            raise
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()[0]
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        emb1 = self.get_embedding(text1).reshape(1, -1)
        emb2 = self.get_embedding(text2).reshape(1, -1)
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def test_symptom_pairs(self, test_pairs: List[Tuple[str, str, str]]):
        """Test multiple symptom pairs and display results"""
        print(f"\n{'='*80}")
        print(f"Testing Symptom Pairs with {self.model_name}")
        print(f"{'='*80}\n")
        
        results = []
        for symptom1, symptom2, relationship in test_pairs:
            similarity = self.compute_similarity(symptom1, symptom2)
            results.append((symptom1, symptom2, relationship, similarity))
            
            # Color code based on relationship
            if relationship == "SIMILAR":
                status = "✓ GOOD" if similarity > 0.7 else "✗ POOR"
            else:  # DIFFERENT
                status = "✓ GOOD" if similarity < 0.5 else "✗ POOR"
            
            print(f"{status} | {similarity:.4f} | {symptom1} ↔ {symptom2} ({relationship})")
        
        print(f"\n{'='*80}\n")
        return results


def run_comprehensive_test():
    """Test multiple models with medical symptom pairs"""
    
    # Define test pairs: (symptom1, symptom2, expected_relationship)
    test_pairs = [
        # Should be SIMILAR (high similarity expected)
        ("headache", "head pain", "SIMILAR"),
        ("dizziness", "unconsciousness", "SIMILAR"),
        ("dizziness", "vertigo", "SIMILAR"),
        ("nausea", "vomiting", "SIMILAR"),
        ("fever", "high temperature", "SIMILAR"),
        ("shortness of breath", "difficulty breathing", "SIMILAR"),
        ("chest pain", "chest discomfort", "SIMILAR"),
        ("fatigue", "tiredness", "SIMILAR"),
        ("joint pain", "arthralgia", "SIMILAR"),
        ("abdominal pain", "stomach pain", "SIMILAR"),
        
        # Should be DIFFERENT (low similarity expected)
        ("headache", "knee pain", "DIFFERENT"),
        ("fever", "fracture", "DIFFERENT"),
        ("dizziness", "rash", "DIFFERENT"),
        ("cough", "numbness", "DIFFERENT"),
        ("nausea", "blurred vision", "DIFFERENT"),
    ]
    
    # Models to test
    models_to_test = [
        # Medical/Biomedical Models
        ("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext", "PubMedBERT"),
        ("emilyalsentzer/Bio_ClinicalBERT", "ClinicalBERT"),
        ("microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext", "BiomedBERT"),
        
        # General-purpose models (for comparison)
        ("sentence-transformers/all-MiniLM-L6-v2", "MiniLM (General)"),
        ("sentence-transformers/all-mpnet-base-v2", "MPNet (General)"),
        
        # Semantic similarity focused models
        ("sentence-transformers/paraphrase-MiniLM-L6-v2", "Paraphrase MiniLM"),
    ]
    
    all_results = {}
    
    for model_id, model_name in models_to_test:
        try:
            tester = ModelTester(model_id)
            results = tester.test_symptom_pairs(test_pairs)
            all_results[model_name] = results
            
            # Calculate scores
            similar_scores = [r[3] for r in results if r[2] == "SIMILAR"]
            different_scores = [r[3] for r in results if r[2] == "DIFFERENT"]
            
            avg_similar = np.mean(similar_scores) if similar_scores else 0
            avg_different = np.mean(different_scores) if different_scores else 0
            separation = avg_similar - avg_different
            
            print(f"\n{'='*80}")
            print(f"SUMMARY FOR {model_name}")
            print(f"{'='*80}")
            print(f"Average similarity for SIMILAR pairs:    {avg_similar:.4f}")
            print(f"Average similarity for DIFFERENT pairs:  {avg_different:.4f}")
            print(f"Separation score:                        {separation:.4f} (higher is better)")
            print(f"{'='*80}\n")
            
            time.sleep(2)  # Pause between models
            
        except Exception as e:
            print(f"\n✗ Failed to test {model_name}: {e}\n")
            continue
    
    # Final comparison
    print(f"\n{'='*80}")
    print(f"FINAL MODEL COMPARISON")
    print(f"{'='*80}\n")
    
    for model_name, results in all_results.items():
        similar_scores = [r[3] for r in results if r[2] == "SIMILAR"]
        different_scores = [r[3] for r in results if r[2] == "DIFFERENT"]
        
        avg_similar = np.mean(similar_scores) if similar_scores else 0
        avg_different = np.mean(different_scores) if different_scores else 0
        separation = avg_similar - avg_different
        
        print(f"{model_name:30} | Separation: {separation:.4f} | Similar: {avg_similar:.4f} | Different: {avg_different:.4f}")
    
    print(f"\n{'='*80}")
    print("RECOMMENDATION: Choose the model with highest separation score")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SEMANTIC MODEL COMPARISON FOR MEDICAL SYMPTOM MATCHING")
    print("="*80)
    print("\nThis script tests multiple transformer models to find the best")
    print("one for matching medical symptoms semantically.")
    print("\nModels will be evaluated on their ability to:")
    print("1. Recognize similar symptoms (e.g., 'headache' ≈ 'head pain')")
    print("2. Distinguish different symptoms (e.g., 'headache' ≠ 'knee pain')")
    print("\n" + "="*80 + "\n")
    
    input("Press Enter to start testing (this will take several minutes)...")
    
    run_comprehensive_test()