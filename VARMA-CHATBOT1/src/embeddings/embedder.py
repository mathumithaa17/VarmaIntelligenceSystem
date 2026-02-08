from sentence_transformers import SentenceTransformer


class VarmaEmbedder:
    """
    Embedding model wrapper for Varma RAG system
    """

    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-base-en")

    def encode(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
