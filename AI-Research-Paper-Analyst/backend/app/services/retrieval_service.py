"""Dense (FAISS) + BM25 retrieval, Reciprocal Rank Fusion, optional cross-encoder reranking."""
from sqlalchemy.orm import Session

from app.config import settings
from app.models.paper import Chunk, Paper
from app.services.embedding_service import embedder
from app.services.vector_store_service import vector_store

RRF_K = 60
_reranker = None


def _rerank(query: str, rows: list[dict]) -> list[dict]:
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder

        _reranker = CrossEncoder(settings.reranker_model)
    scores = _reranker.predict([(query, r["text"]) for r in rows])
    for r, s in zip(rows, scores):
        r["score"] = float(s)
    return sorted(rows, key=lambda r: r["score"], reverse=True)


def retrieve(
    db: Session,
    workspace_id: str,
    query: str,
    k: int | None = None,
    paper_ids: list[str] | None = None,
    mode: str | None = None,       # dense | bm25 | hybrid (default from settings)
    rerank: bool | None = None,
) -> list[dict]:
    k = k or settings.top_k
    mode = mode or ("hybrid" if settings.use_hybrid else "dense")
    rerank = settings.use_reranker if rerank is None else rerank
    cand = 200 if paper_ids else max(50, k * 5)

    rankings: list[list[int]] = []
    if mode in ("dense", "hybrid"):
        qv = embedder.embed_query(query)
        rankings.append([cid for cid, _ in vector_store.dense_search(workspace_id, db, qv, cand)])
    if mode in ("bm25", "hybrid"):
        rankings.append([cid for cid, _ in vector_store.bm25_search(workspace_id, db, query, cand)])

    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + rank + 1)
    if not fused:
        return []

    q = db.query(Chunk, Paper).join(Paper, Paper.id == Chunk.paper_id).filter(
        Chunk.id.in_(list(fused)), Chunk.workspace_id == workspace_id
    )
    if paper_ids:
        q = q.filter(Chunk.paper_id.in_(paper_ids))
    rows = [
        {
            "chunk_id": c.id,
            "paper_id": c.paper_id,
            "paper_title": p.title or p.filename,
            "filename": p.filename,
            "page_start": c.page_start,
            "page_end": c.page_end,
            "section": c.section,
            "text": c.text,
            "score": fused[c.id],
        }
        for c, p in q.all()
    ]
    rows.sort(key=lambda r: r["score"], reverse=True)
    rows = rows[: max(k * 3, k) if rerank else k]
    if rerank and rows:
        rows = _rerank(query, rows)[:k]
    return rows
