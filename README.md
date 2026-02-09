# PDF Knowledge Chat

A simple Retrieval-Augmented Generation (RAG) backend and UI for answering questions over uploaded PDF files.

## Features
- Upload one or more PDFs for ingestion
- PDF text extraction + chunking with overlap
- No external search/RAG libraries
- Semantic search via embeddings + cosine similarity
- Keyword search via simple TF-IDF-like scoring
- Hybrid fusion + lightweight reranking
- Evidence threshold gate -> returns "insufficient evidence"
- Simple chat UI served by FastAPI

## Run locally
1) Create venv and install:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
