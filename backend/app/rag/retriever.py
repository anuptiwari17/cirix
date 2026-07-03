from app.embeddings.vector_store import get_retriever
from app.config import TOP_K_CONTEXT


def retrieve_context(question: str) -> list[dict]:
    """
    Runs similarity search via a fresh LangChain retriever (always bound
    to the current vector store instance, so it survives clear_all()
    recreating the underlying collection) and returns chunks in the
    {text, metadata} shape the rest of the app expects.
    """
    if not question or not question.strip():
        return []

    retriever = get_retriever(TOP_K_CONTEXT)
    docs = retriever.invoke(question)
    return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]