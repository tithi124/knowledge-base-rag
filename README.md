# PDF Knowledge Chat

A lightweight **Retrieval-Augmented Generation (RAG)** system that allows users to upload PDF documents and ask questions grounded strictly in the uploaded knowledge base.  
The system is implemented **from scratch** using **FastAPI** and **Mistral AI**, without relying on any external RAG, search, or vector database libraries.

---

## Overview

This project implements a full RAG pipeline end-to-end:

- PDF ingestion and text extraction
- Chunking with overlap
- Hybrid retrieval (semantic + keyword)
- Lightweight reranking and evidence gating
- Answer generation with citations
- Simple web UI for ingestion and chat

The goal is to demonstrate **core RAG mechanics and reasoning**, rather than hiding complexity behind third-party abstractions.

---

## System Design Details

### 1) Data Ingestion

**Endpoint:** `POST /ingest`

- Accepts one or more PDF files via multipart upload.
- Extracts text using **PyPDF**.
- Splits text into overlapping chunks.
- Generates embeddings for each chunk via **Mistral embeddings**.
- Stores:
  - chunk metadata (JSONL)
  - embeddings (NumPy `.npy`)

#### Chunking Considerations

This project uses fixed-size, overlapping character chunks:

- **Chunk size:** ~1200 characters (configurable)
- **Overlap:** ~200 characters (configurable)

Why overlap:
- Prevents important definitions from being split across chunk boundaries.
- Improves retrieval when the query matches text near a boundary.

Limitations:
- If a PDF is scanned/image-only, `extract_text()` may return little or no text.

---

### 2) Query Processing

**Endpoint:** `POST /query`

#### Intent Detection
A small intent layer prevents unnecessary retrieval for non-knowledge prompts:

- Example: `"hello"` does **not** trigger retrieval.
- Knowledge queries trigger retrieval and generation.

#### Query Rewrite (Retrieval Optimization)
Queries are rewritten to be retrieval-friendly using the LLM:
- Removes filler
- Keeps entities/numbers/keywords
- Produces a short search-optimized query

---

### 3) Semantic Search

- Each chunk embedding is compared with the query embedding using **cosine similarity** (NumPy).
- Produces semantic scores across all chunks.
- Retrieves top candidates by similarity.

No third-party vector DB is used.

---

### 4) Keyword Search

A lightweight TF-IDF-like scoring is implemented from scratch:

- Tokenizes query + chunk text
- Computes document frequency and an IDF term
- Produces keyword relevance scores

This helps catch:
- Exact matches (IDs, acronyms, terms)
- Cases where embeddings underperform

---

### 5) Hybrid Retrieval & Re-ranking

Semantic and keyword results are combined:

- Normalize both score sets
- Compute a weighted hybrid score
- Pull a candidate pool
- Apply a lightweight re-ranker that boosts:
  - query term coverage
  - multi-hit document coherence
  - semantic strength as tie-breaker

This hybrid approach improves robustness compared to semantic-only retrieval.

---

### 6) Evidence Threshold & Refusal

Before generation, the system checks evidence quality:

If the top retrieved chunk’s semantic similarity is below a threshold, the system returns: "insufficient evidence"

This is a hallucination guardrail to avoid unsupported answers.

---

### 7) Answer Generation (Grounded + Citations)

The generation step calls a Mistral chat model with:

- the user’s question
- top-K retrieved evidence snippets labeled `[1]`, `[2]`, ...

The prompt instructs the model to:

- answer **only** using evidence snippets
- cite sources in the answer using `[1]`, `[2]`, ...
- return exactly `"insufficient evidence"` if evidence is not enough

The API response also includes structured citation metadata:
- filename
- page range
- excerpt
- retrieval score

---

## Web UI

The UI is served directly by FastAPI at `/` and supports:

- Uploading PDFs for ingestion
- Chat interface for querying
- Citation rendering for transparency
- Visual “status” feedback for ingestion + query

---

## API Endpoints

### Ingest PDFs

**Request**
```http
POST /ingest
Content-Type: multipart/form-data
````

**Response**

```json
{
  "files_ingested": 1,
  "chunks_added": 12
}
```

---

### Query the Knowledge Base

**Request**

```http
POST /query
Content-Type: application/json
```

```json
{
  "question": "What is safety stock?"
}
```

**Response**

```json
{
  "intent": "knowledge_query",
  "used_search": true,
  "answer": "Safety stock is the minimum inventory reserve kept to protect against demand variability... [1]",
  "citations": [
    {
      "chunk_id": "uuid",
      "filename": "Supply_Chain_Guide.pdf",
      "page_start": 1,
      "page_end": 2,
      "score": 0.91,
      "excerpt": "Safety stock: minimum inventory reserve..."
    }
  ],
  "refusal_reason": null
}
```

---

## Running Locally

### 1) Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Set the Mistral API key

**Option A (recommended): environment variable**

```bash
export MISTRAL_API_KEY="your_api_key_here"
```

**Option B: one-liner**

```bash
MISTRAL_API_KEY="your_api_key_here" uvicorn app.main:app --reload --port 8000
```

### 3) Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

* UI: [http://localhost:8000](http://localhost:8000)
* Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Libraries & Tools Used

* **FastAPI** – API framework
  [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

* **Uvicorn** – ASGI server
  [https://www.uvicorn.org/](https://www.uvicorn.org/)

* **Mistral AI SDK** – embeddings + chat generation
  [https://docs.mistral.ai/](https://docs.mistral.ai/)

* **PyPDF** – PDF text extraction
  [https://pypdf.readthedocs.io/](https://pypdf.readthedocs.io/)

* **NumPy** – vector math + cosine similarity
  [https://numpy.org/](https://numpy.org/)

* **python-multipart** – multipart file uploads for FastAPI
  [https://andrew-d.github.io/python-multipart/](https://andrew-d.github.io/python-multipart/)
