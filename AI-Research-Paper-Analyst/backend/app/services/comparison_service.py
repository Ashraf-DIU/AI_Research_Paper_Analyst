import json

from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.prompts import COMPARISON_SYSTEM
from app.services.extraction_service import get_or_create_analysis
from app.services.llm_service import complete

DIMENSIONS = [
    ("Objective", "research_objective"), ("Methodology", "methodology"), ("Datasets", "datasets"),
    ("Models / architecture", "models"), ("Evaluation metrics", "evaluation_metrics"),
    ("Key results", "key_results"), ("Limitations", "limitations"), ("Future work", "future_work"),
]


def _values(v) -> list[dict]:
    if not v:
        return []
    items = v if isinstance(v, list) else [v]
    return [{"value": i["value"], "page": i.get("page"), "verified": i.get("verified", False)} for i in items]


def compare_papers(db: Session, papers: list[Paper], summarize: bool = True) -> dict:
    analyses = {p.id: get_or_create_analysis(db, p) for p in papers}
    rows = []
    for label, field in DIMENSIONS:
        cells = []
        for p in papers:
            vals = _values(analyses[p.id].get(field))
            # "reported": False means "not extracted", NOT "the paper lacks it".
            cells.append({"paper_id": p.id, "values": vals, "reported": bool(vals)})
        rows.append({"dimension": label, "cells": cells})
    summary = None
    if summarize:
        brief = {p.title or p.filename: {f: [v["value"] for v in _values(analyses[p.id].get(f))]
                                           for _, f in DIMENSIONS} for p in papers}
        summary = complete(COMPARISON_SYSTEM, json.dumps(brief, ensure_ascii=False))
    return {"papers": [{"id": p.id, "title": p.title or p.filename} for p in papers], "rows": rows, "summary": summary}
