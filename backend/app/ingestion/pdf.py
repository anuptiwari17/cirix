import fitz  # PyMuPDF
import uuid
from app.ingestion.chunker import chunk_text
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def process_pdf(file_path: str, original_filename: str) -> dict:
    """
    Extracts text page-by-page from a PDF, chunks it, and builds
    chunk + metadata lists ready for embedding.

    Returns a dict: { source_id, chunks: [str], metadatas: [dict] }
    """
    source_id = str(uuid.uuid4())
    doc = fitz.open(file_path)

    all_chunks = []
    all_metadatas = []

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text()
        if not page_text.strip():
            continue  # skip blank/image-only pages

        page_chunks = chunk_text(page_text, CHUNK_SIZE, CHUNK_OVERLAP)

        for chunk in page_chunks:
            all_chunks.append(chunk)
            all_metadatas.append({
                "source_id": source_id,
                "type": "pdf",
                "file": original_filename,
                "page": page_num,
            })

    doc.close()

    if not all_chunks:
        raise ValueError("No extractable text found in this PDF.")

    return {
        "source_id": source_id,
        "chunks": all_chunks,
        "metadatas": all_metadatas,
    }