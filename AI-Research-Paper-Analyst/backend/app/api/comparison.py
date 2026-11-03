from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import load_papers
from app.schemas.comparison import CompareRequest
from app.services.comparison_service import compare_papers

router = APIRouter(prefix="/api")


@router.post("/compare")
def compare(body: CompareRequest, db: Session = Depends(get_db)):
    papers = load_papers(db, body.workspace_id, body.paper_ids)
    return compare_papers(db, papers, body.summarize)
