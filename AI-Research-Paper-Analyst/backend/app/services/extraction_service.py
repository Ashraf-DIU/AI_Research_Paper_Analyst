from sqlalchemy.orm import Session

from app.models.paper import Paper, PaperAnalysis
from app.prompts import EXTRACTION_SYSTEM
from app.schemas.analysis import Finding, ResearchPaperAnalysis
from app.services.llm_service import complete_json
from app.services.retrieval_service import retrieve
from app.utils.citation_utils import build_context
from app.utils.text_utils import normalize_for_match

FIELD_QUERIES = {
    "title": "title abstract of the paper",
    "research_objective": "research objective aim goal contribution of this paper",
    "methodology": "proposed method architecture approach methodology",
    "datasets": "datasets data collection benchmark training and test data",
    "models": "models architectures baselines compared methods",
    "evaluation_metrics": "evaluation metrics accuracy F1 AUC precision recall BLEU",
    "key_results": "experimental results performance improvement outperforms",
    "limitations": "limitations weaknesses shortcomings",
    "future_work": "future work conclusion future research directions",
}
LIST_FIELDS = ["datasets", "models", "evaluation_metrics", "key_results", "limitations", "future_work"]


def _verify(f: dict | None, texts_by_page: dict[int, str], all_text: str) -> Finding | None:
    if not f or not isinstance(f, dict) or not str(f.get("value", "")).strip():
        return None
    page = f.get("page")
    page = page if isinstance(page, int) and page in texts_by_page else None
    ev = str(f.get("evidence", ""))[:300]
    haystack = normalize_for_match(texts_by_page[page]) if page else all_text
    verified = bool(ev) and normalize_for_match(ev) in haystack
    return Finding(value=str(f["value"])[:600], evidence=ev, page=page, verified=verified)


def analyze_paper(db: Session, paper: Paper) -> dict:
    seen: dict[int, dict] = {}
    for field, q in FIELD_QUERIES.items():
        for c in retrieve(db, paper.workspace_id, q, k=3, paper_ids=[paper.id]):
            seen.setdefault(c["chunk_id"], c)
    chunks = sorted(seen.values(), key=lambda c: c["page_start"])[:18]
    if not chunks:
        raise ValueError("Paper has no indexed text yet.")

    context, _ = build_context(chunks)
    raw = complete_json(EXTRACTION_SYSTEM, f"Excerpts:\n{context}")

    texts_by_page: dict[int, str] = {}
    for c in chunks:
        for p in range(c["page_start"], c["page_end"] + 1):
            texts_by_page[p] = texts_by_page.get(p, "") + " " + c["text"]
    all_text = normalize_for_match(" ".join(texts_by_page.values()))

    data = {}
    for field in ["title", "research_objective", "methodology"]:
        data[field] = _verify(raw.get(field), texts_by_page, all_text)
    for field in LIST_FIELDS:
        items = raw.get(field) or []
        data[field] = [f for f in (_verify(i, texts_by_page, all_text) for i in items if isinstance(i, dict)) if f]

    result = ResearchPaperAnalysis(**data).model_dump()
    row = db.get(PaperAnalysis, paper.id)
    if row:
        row.analysis_json = result
    else:
        db.add(PaperAnalysis(paper_id=paper.id, analysis_json=result))
    db.commit()
    return result


def get_or_create_analysis(db: Session, paper: Paper) -> dict:
    row = db.get(PaperAnalysis, paper.id)
    return row.analysis_json if row else analyze_paper(db, paper)
