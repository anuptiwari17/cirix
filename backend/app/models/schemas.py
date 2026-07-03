from pydantic import BaseModel


class UploadResponse(BaseModel):
    source_id: str
    filename: str
    chunk_count: int
    message: str

class ChatRequest(BaseModel):
    session_id: str
    question: str


class Citation(BaseModel):
    label: str
    text: str
    metadata: dict


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]

class SourceInfo(BaseModel):
    source_id: str
    type: str
    label: str


class DeleteResponse(BaseModel):
    source_id: str
    deleted: bool


class WebsiteUploadRequest(BaseModel):
    url: str


class YoutubeUploadRequest(BaseModel):
    url: str


