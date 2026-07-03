def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    """
    Recursive-ish, sentence-aware chunking.
    Splits on paragraph/sentence boundaries where possible instead of
    cutting mid-sentence, while respecting chunk_size as a soft target.
    """
    text = text.strip()
    if not text:
        return []

    # Rough sentence split — good enough without pulling in nltk/spacy
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            # start new chunk, carrying overlap from the end of the previous one
            if overlap > 0 and current:
                overlap_text = current[-overlap:]
                current = f"{overlap_text} {sentence}".strip()
            else:
                current = sentence

    if current:
        chunks.append(current)

    return chunks