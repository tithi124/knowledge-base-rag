import numpy as np
from typing import List

def cosine_sim_matrix(query_vec: np.ndarray, doc_embs: np.ndarray) -> np.ndarray:
    if doc_embs.shape[0] == 0:
        return np.array([], dtype=np.float32)

    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    d = doc_embs / (np.linalg.norm(doc_embs, axis=1, keepdims=True) + 1e-9)
    return (d @ q).astype(np.float32)

def minmax_normalize(arr: List[float]):
    if not arr:
        return []
    mn, mx = min(arr), max(arr)
    if mx - mn < 1e-9:
        return [0.0 for _ in arr]
    return [(x - mn) / (mx - mn) for x in arr]

def hybrid_scores(sem_scores, kw_scores, w_sem=0.7, w_kw=0.3):
    sem_n = minmax_normalize(list(sem_scores))
    kw_n = minmax_normalize(list(kw_scores))
    return [w_sem * s + w_kw * k for s, k in zip(sem_n, kw_n)]
