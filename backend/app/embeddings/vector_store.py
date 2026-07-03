import chromadb
from app.config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME
        )

    def add_chunks(self, ids: list[str], embeddings: list[list[float]],
                   documents: list[str], metadatas: list[dict]):
        """Add chunk texts + their embeddings + metadata to the store."""
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, query_embedding: list[float], top_k: int):
        """Similarity search — returns top_k closest chunks."""
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

    def delete_by_source(self, source_id: str):
        """Delete all chunks belonging to one source (by metadata filter)."""
        self.collection.delete(where={"source_id": source_id})

    def list_sources(self):
        """Return all unique sources currently stored."""
        results = self.collection.get(include=["metadatas"])
        seen = {}
        for meta in results["metadatas"]:
            sid = meta.get("source_id")
            if sid and sid not in seen:
                seen[sid] = meta
        return list(seen.values())
    

    def clear_all(self):
        """Delete the entire collection and recreate it empty — used for 'Start New Session'."""
        self.client.delete_collection(CHROMA_COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME
        )


# Singleton instance — import this everywhere instead of creating new clients
vector_store = VectorStore()