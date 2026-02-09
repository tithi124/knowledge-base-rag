import math
import re
from collections import Counter, defaultdict
from typing import List, Dict

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")

def tokenize(text: str):
    return [t.lower() for t in TOKEN_RE.findall(text)]

def build_df(chunks: List[Dict]):
    df = defaultdict(int)
    for ch in chunks:
        seen = set(tokenize(ch["text"]))
        for t in seen:
            df[t] += 1
    return df

def keyword_scores(chunks: List[Dict], query: str):
    """
    Simple TF-IDF-like scoring without external search libs.
    """
    q_tokens = tokenize(query)
    if not q_tokens or len(chunks) == 0:
        return [0.0] * len(chunks)

    df = build_df(chunks)
    N = len(chunks)
    q_counts = Counter(q_tokens)

    scores = []
    for ch in chunks:
        c_counts = Counter(tokenize(ch["text"]))
        s = 0.0
        for term, q_tf in q_counts.items():
            tf = c_counts.get(term, 0)
            if tf == 0:
                continue
            idf = math.log((N + 1) / (df.get(term, 0) + 1)) + 1.0
            s += (tf * idf) * q_tf
        scores.append(s)

    return scores
