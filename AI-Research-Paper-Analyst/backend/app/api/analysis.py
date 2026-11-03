from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.paper import Paper, PaperAnalysis
from app.services.extraction_service import analyze_paper

router = APIRouter(prefix="/api")


@router.post("/papers/{paper_id}/analyze")
def analyze(paper_id: str, db: Session = Depends(get_db)):
    p = db.get(Paper, paper_id)
    if not p:
        raise HTTPException(404, "Paper not found")
    if p.status != "ready":
        raise HTTPException(409, f"Paper is {p.status}")
    return analyze_paper(db, p)


@router.get("/papers/{paper_id}/analysis")
def get_analysis(paper_id: str, db: Session = Depends(get_db)):
    row = db.get(PaperAnalysis, paper_id)
    if not row:
        raise HTTPException(404, "No analysis yet. POST /api/papers/{id}/analyze first.")
    return row.analysis_json
