from app.embeddings.embedder import embedder
from app.embeddings.vector_store import vector_store
from app.config import TOP_K_RETRIEVE, TOP_K_CONTEXT


def retrieve_context(question: str) -> list[dict]:
    """
    Embeds the question, searches ChromaDB, and returns the top chunks
    with their text + metadata, ready to feed into the prompt.
    """
    query_vec = embedder.embed_query(question)
    results = vector_store.query(query_embedding=query_vec, top_k=TOP_K_RETRIEVE)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Take only the top TOP_K_CONTEXT to keep the prompt tight
    contexts = []
    for doc, meta in zip(documents[:TOP_K_CONTEXT], metadatas[:TOP_K_CONTEXT]):
        contexts.append({"text": doc, "metadata": meta})

    return contexts