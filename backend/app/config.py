import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Models ---
EMBEDDING_MODEL_NAME = "models/gemini-embedding-001"
LLM_MODEL_NAME = "gemini-2.5-flash"

# --- Chunking ---
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

# --- Retrieval ---
TOP_K_RETRIEVE = 10
TOP_K_CONTEXT = 5

# --- Storage paths ---
CHROMA_DB_DIR = "chroma_db"
CHROMA_COLLECTION_NAME = "sourcechat_docs"
UPLOADS_DIR = "uploads"

# --- Sanity check on startup ---
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Add it to backend/.env")