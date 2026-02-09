from fastapi import APIRouter

from app.core.schemas import QueryRequest, QueryResponse, Citation
from app.core.config import TOP_K, SEMANTIC_MIN_SIM, HYBRID_WEIGHT_SEM, HYBRID_WEIGHT_KW, CHAT_MODEL
from app.storage.local_store import load_index
from app.retrieval.intent import detect_intent, should_search
from app.retrieval.embeddings import embed_query
from app.retrieval.hybrid import cosine_sim_matrix, hybrid_scores
from app.retrieval.keyword import keyword_scores, tokenize
from app.retrieval.rerank import rerank
from app.retrieval.prompt import REWRITE_SYSTEM, ANSWER_SYSTEM
from app.retrieval.policies import policy_refusal_reason
from app.core.mistral_client import get_mistral_client

router = APIRouter()

def rewrite_query(user_q: str) -> str:
    client = get_mistral_client()
    res = client.chat.complete(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": REWRITE_SYSTEM},
            {"role": "user", "content": user_q},
        ],
    )
    return res.choices[0].message.content.strip()

def generate_answer(question: str, snippets):
    client = get_mistral_client()
    evidence = "\n\n".join([f"[{i+1}] {s}" for i, s in enumerate(snippets)])
    user = f"Question:\n{question}\n\nEvidence snippets:\n{evidence}"

    res = client.chat.complete(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": ANSWER_SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    return res.choices[0].message.content.strip()

@router.post("", response_model=QueryResponse)
async def query(req: QueryRequest):
    # Policy gate (bonus points)
    refusal = policy_refusal_reason(req.question)
    if refusal:
        return QueryResponse(
            intent="refused",
            used_search=False,
            answer="insufficient evidence",
            citations=[],
            refusal_reason=refusal,
        )

    intent = detect_intent(req.question)
    if not should_search(intent):
        return QueryResponse(
            intent=intent,
            used_search=False,
            answer="Hey! Upload PDFs first, then ask me questions about them. I’ll answer with citations.",
            citations=[],
        )

    metas, embs = load_index()
    if len(metas) == 0:
        return QueryResponse(
            intent=intent,
            used_search=True,
            answer="insufficient evidence",
            citations=[],
            refusal_reason="No PDFs ingested yet.",
        )

    # Query rewrite for better retrieval
    rewritten = rewrite_query(req.question)

    # Semantic retrieval
    q_emb = embed_query(rewritten)
    sem = cosine_sim_matrix(q_emb, embs)

    # Keyword retrieval
    kw = keyword_scores(metas, rewritten)

    # Hybrid fusion
    hyb = hybrid_scores(sem, kw, w_sem=HYBRID_WEIGHT_SEM, w_kw=HYBRID_WEIGHT_KW)

    # Build candidate list
    candidates = []
    q_tokens = tokenize(rewritten)
    for i, m in enumerate(metas):
        candidates.append({
            **m,
            "sem": float(sem[i]),
            "kw": float(kw[i]),
            "hybrid": float(hyb[i]),
        })

    # Select a pool then rerank
    candidates.sort(key=lambda x: x["hybrid"], reverse=True)
    pool = candidates[: max(20, TOP_K * 4)]
    ranked = rerank(pool, q_tokens)[:TOP_K]

    # Evidence threshold: refuse if top semantic similarity is too low
    top_sem = ranked[0]["sem"] if ranked else 0.0
    if top_sem < SEMANTIC_MIN_SIM:
        return QueryResponse(
            intent=intent,
            used_search=True,
            answer="insufficient evidence",
            citations=[],
            refusal_reason=f"Top similarity {top_sem:.3f} below threshold {SEMANTIC_MIN_SIM:.3f}.",
        )

    # Generate answer using ONLY retrieved evidence
    snippets = [r["text"] for r in ranked]
    answer = generate_answer(req.question, snippets)

    # Build citations
    citations = []
    for r in ranked:
        citations.append(Citation(
            chunk_id=r["chunk_id"],
            filename=r["filename"],
            page_start=r.get("page_start"),
            page_end=r.get("page_end"),
            score=float(r["final"]),
            excerpt=r["text"][:240] + ("..." if len(r["text"]) > 240 else ""),
        ))

    return QueryResponse(
        intent=intent,
        used_search=True,
        answer=answer,
        citations=citations,
    )
