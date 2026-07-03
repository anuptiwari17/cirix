import re
import uuid
import socket
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app.ingestion.chunker import chunk_text
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_video_id(url: str) -> str:
    """
    Extracts an 11-character YouTube video ID from common URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",   # watch?v= or /embed/
        r"youtu\.be\/([0-9A-Za-z_-]{11})",   # short links
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Could not extract a video ID from this YouTube URL.")


def _format_timestamp(seconds: float) -> str:
    """Converts seconds (e.g. 94.5) to 'MM:SS' format."""
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def process_youtube(url: str) -> dict:
    """
    Extracts a transcript from a YouTube URL, groups snippets into
    ~chunk_size blocks, and builds chunk + metadata lists ready for embedding.

    Returns a dict: { source_id, chunks: [str], metadatas: [dict] }
    """
    video_id = extract_video_id(url)
    source_id = str(uuid.uuid4())

    try:
        socket.setdefaulttimeout(15)
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        raise ValueError("No captions available for this video.")
    except socket.timeout:
        raise ValueError("Timed out fetching transcript — YouTube may be rate-limiting requests. Try again in a moment.")
    except Exception:
        raise ValueError("Could not fetch a transcript for this video.")

    snippets = list(fetched)
    if not snippets:
        raise ValueError("No captions available for this video.")

    video_title = f"YouTube video ({video_id})"  # simple placeholder, no extra API call needed

    # Group raw caption snippets into ~chunk_size blocks, keeping the
    # timestamp of the FIRST snippet in each block for citation purposes.
    chunks = []
    metadatas = []
    current_text = ""
    current_start = snippets[0].start

    for snippet in snippets:
        if len(current_text) + len(snippet.text) + 1 <= CHUNK_SIZE:
            current_text = f"{current_text} {snippet.text}".strip()
        else:
            if current_text:
                chunks.append(current_text)
                metadatas.append({
                    "source_id": source_id,
                    "type": "youtube",
                    "video": video_title,
                    "timestamp": _format_timestamp(current_start),
                })
            current_text = snippet.text
            current_start = snippet.start

    if current_text:
        chunks.append(current_text)
        metadatas.append({
            "source_id": source_id,
            "type": "youtube",
            "video": video_title,
            "timestamp": _format_timestamp(current_start),
        })

    return {
        "source_id": source_id,
        "chunks": chunks,
        "metadatas": metadatas,
    }