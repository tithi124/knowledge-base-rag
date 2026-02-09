import numpy as np
from app.core.mistral_client import get_mistral_client
from app.core.config import EMBED_MODEL

def embed_texts(texts):
    """
    Creates embeddings for a list of strings using Mistral embeddings.
    """
    client = get_mistral_client()
    res = client.embeddings.create(model=EMBED_MODEL, inputs=texts)
    vectors = [d.embedding for d in res.data]
    return np.array(vectors, dtype=np.float32)

def embed_query(q: str):
    return embed_texts([q])[0]
