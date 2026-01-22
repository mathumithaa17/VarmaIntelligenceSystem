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

    def retrieve(self, query, top_k=3):
        nq = normalize(query)

        # 1️⃣ Name-based retrieval (guaranteed)
        for v in self.varma_lookup:
            if v["name"] in nq or nq in v["name"]:
                return [v["doc"]]

        # 2️⃣ Semantic fallback
        query_embedding = self.embedder.encode([query])
        _, indices = self.index.search(query_embedding, top_k)

        return [self.docs[i] for i in indices[0]]
