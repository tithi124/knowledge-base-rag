import os
import json
import uuid
from typing import List, Dict, Tuple

import numpy as np
from app.core.config import INDEX_DIR

META_PATH = os.path.join(INDEX_DIR, "chunks.jsonl")
EMB_PATH = os.path.join(INDEX_DIR, "embeddings.npy")

def ensure_dirs():
    os.makedirs(INDEX_DIR, exist_ok=True)

def load_index() -> Tuple[List[Dict], np.ndarray]:
    """
    Loads chunk metadata and embeddings from disk.
    Metadata stored as JSONL, embeddings stored as NPY.
    """
    ensure_dirs()

    metas: List[Dict] = []
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            for line in f:
                metas.append(json.loads(line))

    if os.path.exists(EMB_PATH):
        embs = np.load(EMB_PATH)
    else:
        # unknown dim until first embed; keep empty
        embs = np.zeros((0, 1), dtype=np.float32)

    return metas, embs

def save_index(metas: List[Dict], embs: np.ndarray):
    ensure_dirs()
    with open(META_PATH, "w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    np.save(EMB_PATH, embs)

def add_chunks(file_meta: Dict, chunks: List[Dict], embeddings: np.ndarray) -> int:
    """
    Adds new chunks + embeddings to local index.
    """
    metas, embs = load_index()

    for i, ch in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        metas.append({
            "chunk_id": chunk_id,
            "filename": file_meta["filename"],
            "page_start": ch.get("page_start"),
            "page_end": ch.get("page_end"),
            "text": ch["text"],
        })

    embeddings = embeddings.astype(np.float32)

    if embs.shape[0] == 0:
        embs = embeddings
    else:
        # If your first embs was placeholder shape (0,1), replace it
        if embs.shape[1] == 1 and embeddings.shape[1] != 1:
            embs = embeddings
        else:
            embs = np.vstack([embs, embeddings])

    save_index(metas, embs)
    return len(chunks)
