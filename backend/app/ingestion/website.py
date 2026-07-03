import uuid
import trafilatura
import requests
from bs4 import BeautifulSoup

from app.ingestion.chunker import chunk_text
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def _fallback_extract(url: str) -> tuple[str, str]:
    """BS4 fallback if Trafilatura returns nothing. Returns (title, text)."""
    response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else url

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return title, text


def process_website(url: str) -> dict:
    """
    Extracts readable text from a URL (Trafilatura primary, BS4 fallback),
    chunks it, and builds chunk + metadata lists ready for embedding.

    Returns a dict: { source_id, chunks: [str], metadatas: [dict] }
    """
    source_id = str(uuid.uuid4())

    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded) if downloaded else None
    title = None

    if downloaded:
        metadata = trafilatura.extract_metadata(downloaded)
        if metadata and metadata.title:
            title = metadata.title

    if not text or not text.strip():
        # Trafilatura failed — fall back to BeautifulSoup
        title, text = _fallback_extract(url)

    if not title:
        title = url

    if not text or not text.strip():
        raise ValueError("Could not extract any readable text from this URL.")

    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

    if not chunks:
        raise ValueError("No content found to chunk from this URL.")

    metadatas = [
        {"source_id": source_id, "type": "website", "title": title, "url": url}
        for _ in chunks
    ]

    return {
        "source_id": source_id,
        "chunks": chunks,
        "metadatas": metadatas,
    }