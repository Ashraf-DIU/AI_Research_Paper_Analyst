import json

from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.prompts import GAP_SYSTEM
from app.services.comparison_service import DIMENSIONS, _values
from app.services.extraction_service import get_or_create_analysis
from app.services.llm_service import complete_json
from app.services.retrieval_service import retrieve
from app.utils.citation_utils import build_context

GAP_QUERIES = [
    "datasets used evaluation data single dataset", "external validation generalization to other datasets",
    "evaluation metrics used", "explainability interpretability", "computational cost efficiency parameters",
    "robustness noise adversarial", "reproducibility code availability hyperparameters", "limitations future work",
]
QUALIFICATION = ("This gap is supported only by the uploaded paper collection. It is not proof that no other "
                 "published research has addressed the problem.")


def find_gaps(db: Session, workspace_id: str, papers: list[Paper]) -> dict:
    ids = [p.id for p in papers]
    seen: dict[int, dict] = {}
    for q in GAP_QUERIES:
        for c in retrieve(db, workspace_id, q, k=3, paper_ids=ids):
            seen.setdefault(c["chunk_id"], c)
    chunks = list(seen.values())[:20]
    context, sources = build_context(chunks, max_chars=900)
    brief = {p.title or p.filename: {f: [v["value"] for v in _values(get_or_create_analysis(db, p).get(f))]
                                       for _, f in DIMENSIONS} for p in papers}
    raw = complete_json(GAP_SYSTEM, f"Per-paper analyses (empty = not extracted):\n"
                                    f"{json.dumps(brief, ensure_ascii=False)}\n\nSources:\n{context}")
    gaps = []
    for g in raw.get("gaps", []):
        ev = [sources[s] for s in g.get("evidence", []) if s in sources]
        if not ev:
            continue  # unsupported gaps are dropped
        n_papers = len({e["paper_id"] for e in ev})
        conf = g.get("confidence", "low")
        if n_papers < 2 and conf != "low":
            conf = "low"
        gaps.append({
            "dimension": g.get("dimension", ""), "gap": g.get("gap", ""),
            "possible_direction": g.get("possible_direction", ""), "confidence": conf,
            "evidence": [{"paper_id": e["paper_id"], "paper_title": e["paper_title"],
                          "page_start": e["page_start"], "page_end": e["page_end"],
                          "snippet": e["text"][:250]} for e in ev],
            "qualification": QUALIFICATION,
        })
    return {"gaps": gaps}
