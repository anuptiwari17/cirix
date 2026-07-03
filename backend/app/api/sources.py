from fastapi import APIRouter

from app.embeddings import vector_store
from app.rag.prompt import format_source_label
from app.models.schemas import SourceInfo, DeleteResponse

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceInfo])
async def list_sources():
    raw_sources = vector_store.list_sources()
    return [
        SourceInfo(
            source_id=meta["source_id"],
            type=meta["type"],
            label=format_source_label(meta),
        )
        for meta in raw_sources
    ]


@router.delete("")
async def start_new_session():
    """Wipes all sources — used when the user clicks 'Start New Session' before a fresh upload batch."""
    vector_store.clear_all()
    return {"message": "All sources cleared. Ready for a new session."}


@router.delete("/{source_id}")
async def delete_source(source_id: str):
    vector_store.delete_by_source(source_id)
    return DeleteResponse(source_id=source_id, deleted=True)