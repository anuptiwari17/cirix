from fastapi import APIRouter, HTTPException

from app.rag.chain import run_chat
from app.models.schemas import ChatRequest, ChatResponse, Citation

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = run_chat(request.session_id, request.question)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    citations = [Citation(**c) for c in result["citations"]]
    return ChatResponse(answer=result["answer"], citations=citations)