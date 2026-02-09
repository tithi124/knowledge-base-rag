import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_ingest import router as ingest_router
from app.api.routes_query import router as query_router
from app.core.config import UPLOAD_DIR

app = FastAPI(title="PDF Knowledge Chat")

app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(query_router, prefix="/query", tags=["query"])

# Serve UI
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory="app/ui", html=True), name="ui")
