import pickle
import re
from src.embeddings.embedder import VarmaEmbedder


def normalize(text: str) -> str:
    text = text.lower().replace("_", " ")
    return re.sub(r"\s+", " ", text).strip()


class VarmaRetriever:
    def __init__(self, index_path="varma_index.pkl"):
        with open(index_path, "rb") as f:
            self.index, self.docs = pickle.load(f)

        self.embedder = VarmaEmbedder()

        # Build name lookup
        self.varma_lookup = []
        for d in self.docs:
            text = d.get("text", "")
            for line in text.splitlines():
                if line.lower().startswith("varma name"):
                    name = line.split(":", 1)[-1].strip()
                    self.varma_lookup.append({
                        "name": normalize(name),
                        "doc": d
                    })

    def retrieve(self, query, top_k=15):
        nq = normalize(query)
        # Split query into important words
        query_words = [w for w in nq.split() if len(w) > 3]
        
        # Generate variations for robust matching (e.g. "abdominal" -> "abdomen")
        variations = set(query_words)
        for w in query_words:
            if w.endswith("s"): variations.add(w[:-1])       # hallucinations -> hallucination
            if w.endswith("al"): variations.add(w[:-2])      # abdominal -> abdomen
            if w.endswith("ic"): variations.add(w[:-2])      # diabetic -> diabet
            if w.endswith("ia"): variations.add(w[:-2])      # dyspepsia -> dyspeps

        candidates = []
        seen_ids = set()

        # 1️⃣ Name-based retrieval (High Priority)
        for v in self.varma_lookup:
            if v["name"] in nq or nq in v["name"]:
                doc_id = v["doc"].get("id")
                if doc_id not in seen_ids:
                    candidates.append({"doc": v["doc"], "score": 200.0})
                    seen_ids.add(doc_id)

        # 2️⃣ Semantic Search (Broader Context)
        query_embedding = self.embedder.encode([query])
        # Fetch generous candidates for re-ranking
        D, indices = self.index.search(query_embedding, top_k * 5)
        
        for dist, idx in zip(D[0], indices[0]):
            if idx < len(self.docs):
                doc = self.docs[idx]
                doc_id = doc.get("id")
                if doc_id not in seen_ids:
                    candidates.append({"doc": doc, "score": float(1.0 / (dist + 1e-5))})
                    seen_ids.add(doc_id)
        
        # 3️⃣ Keyword Re-Ranking (Robust)
        for item in candidates:
            text_lower = item["doc"]["text"].lower()
            
            # Boost for any variation match
            match_score = 0
            for var in variations:
                if var in text_lower:
                    match_score += 10.0
                    # Super Boost for Pathognomic/Indications
                    if "pathognomic" in text_lower:
                        snippet = text_lower.split("pathognomic")[1][:300]
                        if var in snippet: match_score += 100.0
                    if "indication" in text_lower:
                        snippet = text_lower.split("indication")[1][:300]
                        if var in snippet: match_score += 50.0
            
            item["score"] += match_score
                
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top_k docs
        return [c["doc"] for c in candidates[:top_k]]
