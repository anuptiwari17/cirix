from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL_NAME


class Embedder:
    def __init__(self):
        # Downloads the model once (~130MB), caches locally after that
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of chunk texts for storage."""
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,  # cosine similarity works cleanly this way
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string for retrieval."""
        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding[0].tolist()


# Singleton — model loads once at import time, not per-request
embedder = Embedder()