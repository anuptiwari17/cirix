from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME
from app.embeddings.embedder import embedder

_vector_store = Chroma(
    collection_name=CHROMA_COLLECTION_NAME,
    embedding_function=embedder,
    persist_directory=CHROMA_DB_DIR,
)


def get_retriever(k: int):
    """Returns a LangChain retriever bound to the current vector store."""
    return _vector_store.as_retriever(search_kwargs={"k": k})


def add_chunks(ids: list[str], documents: list[str], metadatas: list[dict]):
    """
    Stores chunks. Embedding happens internally via `embedder`
    (the embedding_function passed to Chroma above) -- callers pass raw
    text, not precomputed vectors.
    """
    if not documents:
        return  # defensive: adapters should already guard against this, but stay safe
    docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(documents, metadatas)
    ]
    _vector_store.add_documents(documents=docs, ids=ids)


def delete_by_source(source_id: str):
    _vector_store.delete(where={"source_id": source_id})


def clear_all():
    """Deletes the entire collection and recreates it empty."""
    global _vector_store
    _vector_store.delete_collection()
    _vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embedder,
        persist_directory=CHROMA_DB_DIR,
    )


def list_sources() -> list[dict]:
    results = _vector_store.get(include=["metadatas"])
    seen = {}
    for meta in results["metadatas"]:
        sid = meta.get("source_id")
        if sid and sid not in seen:
            seen[sid] = meta
    return list(seen.values())