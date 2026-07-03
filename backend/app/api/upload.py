import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.ingestion.pdf import process_pdf
from app.embeddings.embedder import embedder
from app.embeddings.vector_store import vector_store
from app.models.schemas import UploadResponse
from app.config import UPLOADS_DIR

from app.ingestion.website import process_website
from app.models.schemas import WebsiteUploadRequest

from app.ingestion.youtube import process_youtube
from app.models.schemas import YoutubeUploadRequest


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    # Save uploaded file temporarily
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    saved_path = os.path.join(UPLOADS_DIR, file.filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = process_pdf(saved_path, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Embed + store
    vectors = embedder.embed_texts(result["chunks"])
    ids = [f"{result['source_id']}-{i}" for i in range(len(result["chunks"]))]

    vector_store.add_chunks(
        ids=ids,
        embeddings=vectors,
        documents=result["chunks"],
        metadatas=result["metadatas"],
    )

    return UploadResponse(
        source_id=result["source_id"],
        filename=file.filename,
        chunk_count=len(result["chunks"]),
        message="PDF processed and stored successfully.",
    )



@router.post("/website", response_model=UploadResponse)
async def upload_website(request: WebsiteUploadRequest):
    try:
        result = process_website(request.url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

    vectors = embedder.embed_texts(result["chunks"])
    ids = [f"{result['source_id']}-{i}" for i in range(len(result["chunks"]))]

    vector_store.add_chunks(
        ids=ids,
        embeddings=vectors,
        documents=result["chunks"],
        metadatas=result["metadatas"],
    )

    return UploadResponse(
        source_id=result["source_id"],
        filename=request.url,
        chunk_count=len(result["chunks"]),
        message="Website processed and stored successfully.",
    )


@router.post("/youtube", response_model=UploadResponse)
async def upload_youtube(request: YoutubeUploadRequest):
    try:
        result = process_youtube(request.url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    vectors = embedder.embed_texts(result["chunks"])
    ids = [f"{result['source_id']}-{i}" for i in range(len(result["chunks"]))]

    vector_store.add_chunks(
        ids=ids,
        embeddings=vectors,
        documents=result["chunks"],
        metadatas=result["metadatas"],
    )

    return UploadResponse(
        source_id=result["source_id"],
        filename=request.url,
        chunk_count=len(result["chunks"]),
        message="YouTube video processed and stored successfully.",
    )


