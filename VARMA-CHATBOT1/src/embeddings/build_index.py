import faiss
import numpy as np
import pickle
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.load_json import load_varma_json
from embeddings.embedder import VarmaEmbedder


def varma_to_text(varma: dict) -> str:
    """
    Convert a single Varma record (dict) into structured text
    for embedding and retrieval.
    """
    parts = []

    if varma.get("varmaName"):
        parts.append(f"Varma Name: {varma['varmaName']}")

    if varma.get("varmamType"):
        parts.append(f"Type: {varma['varmamType']}")

    if varma.get("surfaceAnatomy"):
        parts.append(f"Surface Anatomy: {varma['surfaceAnatomy']}")

    if varma.get("indications"):
        parts.append(f"Indications: {varma['indications']}")

    if varma.get("signs"):
        parts.append(f"Signs: {varma['signs']}")

    if varma.get("pathognomicSign"):
        parts.append(f"Pathognomonic Sign: {varma['pathognomicSign']}")

    if varma.get("laterality"):
        parts.append(f"Laterality: {varma['laterality']}")

    if varma.get("synonyms"):
        parts.append(f"Synonyms: {varma['synonyms']}")

    if varma.get("tamilLiterature"):
        parts.append(f"Tamil Literature: {varma['tamilLiterature']}")

    if isinstance(varma.get("anatomicalRelations"), dict):
        for k, v in varma["anatomicalRelations"].items():
            parts.append(f"{k.capitalize()}: {v}")

    return "\n".join(parts)


def build_index():
    # Load JSON → list of dicts
    varma_list = load_varma_json("data/varma_data.json")

    texts = [varma_to_text(v) for v in varma_list]

    embedder = VarmaEmbedder()
    embeddings = embedder.encode(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    with open("varma_index.pkl", "wb") as f:
        pickle.dump((index, varma_list), f)

    print("✅ FAISS index built successfully")


if __name__ == "__main__":
    build_index()
