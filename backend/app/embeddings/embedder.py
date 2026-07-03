from langchain_huggingface import HuggingFaceEmbeddings
from app.config import EMBEDDING_MODEL_NAME

embedder = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"model_kwargs": {"low_cpu_mem_usage": False}},
    encode_kwargs={"normalize_embeddings": True},
)