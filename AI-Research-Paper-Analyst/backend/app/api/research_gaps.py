from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import load_papers
from app.schemas.chat import GapRequest
from app.services.gap_analysis_service import find_gaps

router = APIRouter(prefix="/api")


@router.post("/research-gaps")
def research_gaps(body: GapRequest, db: Session = Depends(get_db)):
    papers = load_papers(db, body.workspace_id, body.paper_ids)
    return find_gaps(db, body.workspace_id, papers)
