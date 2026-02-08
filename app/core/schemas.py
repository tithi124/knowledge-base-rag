from pydantic import BaseModel
from typing import List, Optional

class IngestResponse(BaseModel):
    files_ingested: int
    chunks_added: int

class QueryRequest(BaseModel):
    question: str

class Citation(BaseModel):
    chunk_id: str
    filename: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    score: float
    excerpt: str

class QueryResponse(BaseModel):
    intent: str
    used_search: bool
    answer: str
    citations: List[Citation]
    refusal_reason: Optional[str] = None
