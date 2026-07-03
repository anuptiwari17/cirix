def format_source_label(metadata: dict) -> str:
    """Turns metadata into a human-readable citation label."""
    if metadata["type"] == "pdf":
        return f"{metadata['file']} · p.{metadata['page']}"
    elif metadata["type"] == "website":
        return f"{metadata['title']}"
    elif metadata["type"] == "youtube":
        return f"{metadata['video']} · {metadata['timestamp']}"
    return "Unknown source"


def build_prompt(question: str, contexts: list[dict], chat_history: list[dict] = None) -> str:
    """
    Builds the final prompt sent to Gemini, with numbered sources
    the model is instructed to cite inline.
    """
    context_blocks = []
    for i, ctx in enumerate(contexts, start=1):
        label = format_source_label(ctx["metadata"])
        context_blocks.append(f"[{i}] Source: {label}\n{ctx['text']}")

    context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant context found."

    history_text = ""
    if chat_history:
        history_lines = [f"{turn['role']}: {turn['content']}" for turn in chat_history]
        history_text = "Previous conversation:\n" + "\n".join(history_lines) + "\n\n"

    prompt = f"""You are a helpful assistant that answers questions using ONLY the provided sources.

Rules:
- Answer using only the information in the sources below.
- Cite sources inline using their number, like [1] or [2], right after the claim they support.
- If the sources don't contain the answer, say so clearly instead of guessing.
- Be concise and direct.

{history_text}Sources:
{context_text}

Question: {question}

Answer:"""

    return prompt