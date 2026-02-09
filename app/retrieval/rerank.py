from collections import Counter
from typing import List, Dict

def rerank(results: List[Dict], query_tokens: List[str]):
    """
    Lightweight reranker:
    - boosts keyword coverage
    - tiny coherence bonus for multiple hits from same file
    - uses semantic as a tie-breaker
    """
    unique_q = list(set(query_tokens))

    for r in results:
        text = r["text"].lower()
        covered = sum(1 for t in unique_q if t in text)
        coverage_bonus = covered / max(1, len(unique_q))

        r["final"] = float(r["hybrid"]) + 0.10 * coverage_bonus + 0.05 * float(r["sem"])

    counts = Counter(r["filename"] for r in results)
    for r in results:
        if counts[r["filename"]] >= 2:
            r["final"] += 0.03

    return sorted(results, key=lambda x: x["final"], reverse=True)
