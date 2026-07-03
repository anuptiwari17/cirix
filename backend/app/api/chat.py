from fastapi import APIRouter

from app.rag.retriever import retrieve_context
from app.rag.prompt import build_prompt, format_source_label
from app.rag.generator import generate_answer
from app.rag.memory import get_history, add_turn
from app.models.schemas import ChatRequest, ChatResponse, Citation

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    history = get_history(request.session_id)
    contexts = retrieve_context(request.question)

    prompt = build_prompt(request.question, contexts, history)
    answer = generate_answer(prompt)

    add_turn(request.session_id, "user", request.question)
    add_turn(request.session_id, "assistant", answer)

    citations = [
        Citation(
            label=format_source_label(ctx["metadata"]),
            text=ctx["text"][:200],  # preview only
            metadata=ctx["metadata"],
        )
        for ctx in contexts
    ]

    return ChatResponse(answer=answer, citations=citations)