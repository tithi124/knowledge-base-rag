import os
from typing import List

from fastapi import APIRouter, UploadFile, File
from app.core.config import UPLOAD_DIR, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS
from app.core.schemas import IngestResponse
from app.ingest.pdf_extract import extract_pdf_text_and_pages
from app.ingest.chunking import chunk_text
from app.retrieval.embeddings import embed_texts
from app.storage.local_store import add_chunks

router = APIRouter()

@router.post("", response_model=IngestResponse)
async def ingest_pdfs(files: List[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    files_ingested = 0
    chunks_added = 0

    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            continue

        out_path = os.path.join(UPLOAD_DIR, f.filename)
        content = await f.read()
        with open(out_path, "wb") as w:
            w.write(content)

        files_ingested += 1

        pages = extract_pdf_text_and_pages(out_path)
        chunks = chunk_text(pages, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS)

        texts = [c["text"] for c in chunks]
        if not texts:
            continue

        embs = embed_texts(texts)
        chunks_added += add_chunks({"filename": f.filename}, chunks, embs)

    return IngestResponse(files_ingested=files_ingested, chunks_added=chunks_added)
